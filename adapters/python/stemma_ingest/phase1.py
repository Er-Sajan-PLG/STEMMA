import hashlib
import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import yaml

ROOT = Path(__file__).resolve().parent.parent.parent.parent
PROPOSALS_DIR = (ROOT / "proposals").resolve()

@dataclass
class SourceArtifact:
    source_id: str
    source_version_id: str
    content_hash: str
    size_bytes: int
    media_type: str
    acquired_at: str
    original_path: str
    raw_bytes: bytes

@dataclass
class EvidenceWindow:
    id: str
    source_version_id: str
    document_node_id: str
    page_start: int
    page_end: int
    locator: str
    text: str
    text_hash: str

def get_parser_version() -> str:
    try:
        res = subprocess.run(["pdftotext", "-v"], capture_output=True, text=True)
        # pdftotext typically prints version to stderr
        output = res.stderr if res.stderr else res.stdout
        first_line = output.strip().split("\n")[0]
        return first_line
    except Exception:
        return "unknown"

def detect_mime_type_from_bytes(data: bytes, path: Path) -> tuple[str, bool]:
    # Check magic numbers for common types
    if data.startswith(b"%PDF-"):
        return "application/pdf", True
    # Basic fallbacks (not robust MIME, but better than pure extension)
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png", False
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg", False
    # If not detected by magic, explicitly classify as extension-derived
    ext = path.suffix.lower()
    if ext in [".md", ".txt"]: return "text/plain (extension-derived)", False
    return "application/octet-stream (extension-derived)", False

def acquire_source(path_str: str) -> SourceArtifact:
    path = Path(path_str).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Source not found: {path_str}")
    if not path.is_file():
        raise ValueError(f"Source is not a regular file: {path_str}")
    
    content = path.read_bytes()
    content_hash = f"sha256:{hashlib.sha256(content).hexdigest()}"
    size = len(content)
    now = datetime.now(timezone.utc).isoformat()
    
    mime, is_pdf = detect_mime_type_from_bytes(content, path)
    if not is_pdf:
        # Phase 1 only strictly supports PDF right now
        raise ValueError(f"INVALID_SOURCE: Magic bytes do not indicate a valid PDF: {path_str}")
    
    return SourceArtifact(
        source_id=f"stemma:src.ingest_{int(time.time())}",
        source_version_id=content_hash,
        content_hash=content_hash,
        size_bytes=size,
        media_type=mime,
        acquired_at=now,
        original_path=str(path),
        raw_bytes=content
    )

def extract_physical_page_count(data: bytes) -> int:
    try:
        res = subprocess.run(["pdfinfo", "-"], input=data, capture_output=True)
        if res.returncode == 0:
            match = re.search(r"^Pages:\s+(\d+)", res.stdout.decode('utf-8', 'replace'), re.MULTILINE)
            if match:
                return int(match.group(1))
    except Exception:
        pass
    return -1

def extract_text_pages(data: bytes) -> list[str]:
    res = subprocess.run(["pdftotext", "-layout", "-", "-"], input=data, capture_output=True)
    if res.returncode != 0:
        raise RuntimeError(f"pdftotext failed: {res.stderr.decode('utf-8', 'replace')}")
    
    pages = res.stdout.decode('utf-8', 'replace').split("\x0c")
    if pages and not pages[-1].strip():
        pages = pages[:-1]
    return pages
    
    pages = res.stdout.split("\x0c")
    if pages and not pages[-1].strip():
        pages = pages[:-1]

def process_document(source: SourceArtifact) -> tuple[dict, list[EvidenceWindow]]:
    physical_page_count = extract_physical_page_count(source.raw_bytes)
    parser_version = get_parser_version()
    
    try:
        pages = extract_text_pages(source.raw_bytes)
        text_pages_detected = sum(1 for p in pages if p.strip())
        
        if text_pages_detected == 0 and physical_page_count > 0:
            parser_status = "NO_TEXT_LAYER"
        else:
            parser_status = "PARSE_SUCCESS"
    except Exception as e:
        pages = []
        parser_status = f"PARSE_FAILED: {str(e)}"
        text_pages_detected = 0
        
    manifest = {
        "format": "pdf",
        "parser": {
            "name": "pdftotext",
            "version": parser_version
        },
        "physical_page_count": physical_page_count,
        "extracted_text_page_count": text_pages_detected,
        "text_extracted": text_pages_detected > 0,
        "status": parser_status
    }
    
    windows = []
    
    if parser_status == "PARSE_SUCCESS":
        for page_idx, page_text in enumerate(pages):
            page_num = page_idx + 1
            if not page_text.strip():
                continue
                
            paragraphs = [p.strip() for p in page_text.split("\n\n") if p.strip()]
            for para_idx, para_text in enumerate(paragraphs):
                text_hash = f"sha256:{hashlib.sha256(para_text.encode('utf-8')).hexdigest()}"
                
                # Deterministic Evidence ID
                id_material = f"{source.source_version_id}:{page_num}:{para_idx}"
                window_id = f"win_{hashlib.sha256(id_material.encode()).hexdigest()[:16]}"
                
                win = EvidenceWindow(
                    id=window_id,
                    source_version_id=source.source_version_id,
                    document_node_id=f"page_{page_num}",
                    page_start=page_num,
                    page_end=page_num,
                    locator=f"Page {page_num}, Block {para_idx + 1}",
                    text=para_text,
                    text_hash=text_hash
                )
                windows.append(win)
            
    return manifest, windows

def stage_proposal(run_id: str, source: SourceArtifact, manifest: dict, windows: list[EvidenceWindow], output_filename: str) -> Path:
    # Safely resolve the output path
    raw_out_path = PROPOSALS_DIR / output_filename
    if raw_out_path.is_symlink():
        raise PermissionError(f"Unsafe output path: {raw_out_path} is a symlink.")
    out_path = raw_out_path.resolve()
    
    # Must explicitly be within the proposals directory
    if not out_path.is_relative_to(PROPOSALS_DIR):
        raise PermissionError(f"Unsafe output path: {out_path} escapes proposals directory")
        
    if out_path.exists() and out_path.stat().st_nlink > 1:
        raise PermissionError(f"Unsafe output path: {out_path} is a hard-link alias.")
        
    proposal = {
        "run": {
            "run_id": run_id,
            "pipeline_version": "phase1-1.1",
            "started_at": source.acquired_at,
            "completed_at": datetime.now(timezone.utc).isoformat()
        },
        "source": {
            "source_id": source.source_id,
            "source_version_id": source.source_version_id,
            "content_hash": source.content_hash,
            "size_bytes": source.size_bytes,
            "media_type": source.media_type,
            "original_path": source.original_path
        },
        "document": manifest,
        "evidence_windows": [
            {
                "id": w.id,
                "document_node_id": w.document_node_id,
                "page_start": w.page_start,
                "page_end": w.page_end,
                "locator": w.locator,
                "text": w.text,
                "text_hash": w.text_hash
            } for w in windows
        ],
        "status": "SUCCESS" if windows else manifest["status"]
    }
    
    with out_path.open("x", encoding="utf-8") as f:
        yaml.safe_dump(proposal, f, sort_keys=False)
        
    return out_path

def run_phase1(source_path: str, output_filename: Optional[str] = None) -> tuple[str, str, int, str]:
    if not output_filename:
        run_id = f"ingest_{hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]}"
        output_filename = f"{run_id}.proposal.yaml"
    else:
        run_id = output_filename.replace(".proposal.yaml", "")
        
    source = acquire_source(source_path)
    manifest, windows = process_document(source)
    
    out_path = stage_proposal(run_id, source, manifest, windows, output_filename)
    
    final_status = "SUCCESS" if windows else manifest["status"]
    
    print(f"RUN_ID: {run_id}")
    print(f"SOURCE_HASH: {source.content_hash}")
    print(f"EVIDENCE_WINDOWS: {len(windows)}")
    print(f"STATUS: {final_status}")
    print(f"PROPOSAL_PATH: {out_path}")
    
    return run_id, source.content_hash, len(windows), final_status

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <source_pdf>")
        sys.exit(1)
    try:
        run_phase1(sys.argv[1])
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)
