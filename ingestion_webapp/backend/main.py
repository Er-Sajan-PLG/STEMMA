"""
STEMMA Ingestion Webapp - FastAPI Backend
Upload PDFs, extract evidence, create proposals for human review.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import uuid
import yaml
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn

# STEMMA imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from scripts import ingest
from scripts import curation_pipeline
from scripts import ingest_to_proposals
from scripts.curation_pipeline import GateResult, DraftCallback

# Configuration
ROOT = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = ROOT / "ingestion_webapp" / "uploads"
PROPOSALS_DIR = ROOT / "ingestion_webapp" / "proposals"
PROCESSED_DIR = ROOT / "ingestion_webapp" / "processed"
EXPORT_DIR = ROOT / "exports"

# Ensure directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Models
class UploadResponse(BaseModel):
    file_id: str
    filename: str
    size: int
    status: str
    message: str

class ExtractionResult(BaseModel):
    file_id: str
    kind: str
    pages: int
    is_scanned: bool
    ocr_used: bool
    char_count: int
    text_preview: str
    source_candidate: Dict[str, Any]

class ProposalRequest(BaseModel):
    file_id: str
    kind: str = "entity"  # entity, connection, source
    draft_callback: Optional[str] = None  # module:function for LLM draft
    submitter: Optional[str] = "sajan"
    use_llm: Optional[bool] = False
    provider: Optional[str] = "google"
    model_name: Optional[str] = "antigravity-gemini-3.7-flash"
    api_key: Optional[str] = None

class ProposalResponse(BaseModel):
    proposal_id: str
    file_id: str
    status: str
    decision: str
    publishable: bool
    gates: List[Dict[str, Any]]
    artifact: Optional[Dict[str, Any]]
    reason: str

class ProposalListItem(BaseModel):
    proposal_id: str
    filename: str
    created_at: str
    status: str
    decision: str
    kind: str
    submitter: Optional[str] = "sajan"

class ReviewAction(BaseModel):
    action: str  # "accept", "canonicalize", "reject"
    reviewer: str
    reviewer_role: Optional[str] = "founder"
    reason: Optional[str] = None

class ArtifactUpdateRequest(BaseModel):
    artifact: Dict[str, Any]
    editor: Optional[str] = "sajan"

class HealthResponse(BaseModel):
    status: str
    version: str
    stemma_root: str

# In-memory job tracking (replace with Redis/DB in production)
jobs: Dict[str, Dict[str, Any]] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Starting STEMMA Ingestion Webapp")
    print(f"STEMMA Root: {ROOT}")
    print(f"Upload Dir: {UPLOAD_DIR}")
    print(f"Proposals Dir: {PROPOSALS_DIR}")
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title="STEMMA Ingestion Webapp",
    description="Upload PDFs, extract evidence, create proposals for human review",
    version="0.1.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve Single-Page Ingestion Webapp UI
STATIC_DIR = ROOT / "ingestion_webapp" / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static_files")

@app.get("/", include_in_schema=False)
async def root():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return RedirectResponse(url="/docs")

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        version="0.1.0",
        stemma_root=str(ROOT)
    )

@app.get("/api/llm/models")
async def get_llm_models(provider: str = "google", api_key: Optional[str] = None, free_only: bool = True):
    """Fetch available models from LLM providers (Google Antigravity, OpenRouter, NVIDIA, OpenCode)."""
    from ingestion_webapp.backend import llm_draft
    models = llm_draft.fetch_provider_models(provider=provider, api_key=api_key, free_only=free_only)
    return {"provider": provider, "free_only": free_only, "count": len(models), "models": models}

@app.post("/api/upload", response_model=UploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    source_type: str = Form(default="other"),
    title: Optional[str] = Form(default=None),
    authors: Optional[str] = Form(default=None),
    year: Optional[int] = Form(default=None),
    doi: Optional[str] = Form(default=None),
    license: str = Form(default="CC BY 4.0"),
    publisher: Optional[str] = Form(default=None),
    submitter: str = Form(default="sajan"),
):
    """Upload a PDF or image file for ingestion."""
    # Validate file type
    allowed_extensions = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"}
    file_ext = Path(file.filename).suffix.lower()
    if not file_ext:
        raise HTTPException(400, "File has no extension")
    file_ext = file_ext.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(400, f"Unsupported file type: {file_ext}. Allowed: {allowed_extensions}")
    
    # Generate file ID
    file_id = str(uuid.uuid4())[:8]
    safe_filename = f"{file_id}{file_ext}"
    file_path = UPLOAD_DIR / safe_filename
    
    # Save file
    content = await file.read()
    file_path.write_bytes(content)
    
    # Create source candidate metadata
    source_data = {
        "id": f"lhs:src.ingest-{file_id}",
        "type": "source",
        "title": title or file.filename,
        "kind": "ingested-document",
        "format": "pdf" if file_ext == ".pdf" else "image",
        "source_type": source_type,
        "license": license,
        "lifecycle": "active",
        "accessed_at": datetime.now(timezone.utc).isoformat(),
    }
    if authors:
        source_data["authors"] = [a.strip() for a in authors.split(",")]
    if year:
        source_data["year"] = year
    if doi:
        source_data["doi"] = doi
    if publisher:
        source_data["publisher"] = publisher
    
    # Save source metadata
    source_path = UPLOAD_DIR / f"{file_id}.source.yaml"
    source_path.write_text(yaml.safe_dump(source_data, sort_keys=False, allow_unicode=True))
    
    # Track job
    jobs[file_id] = {
        "status": "uploaded",
        "submitter": submitter,
        "file_path": str(file_path),
        "source_path": str(source_path),
        "source_data": source_data,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    
    return UploadResponse(
        file_id=file_id,
        filename=file.filename,
        size=len(content),
        status="uploaded",
        message="File uploaded successfully. Ready for extraction."
    )

@app.post("/api/extract/{file_id}", response_model=ExtractionResult)
async def extract_file(file_id: str, ocr_max_pages: int = Form(default=50)):
    """Extract text from uploaded document using STEMMA's ingestion pipeline."""
    if file_id not in jobs:
        raise HTTPException(404, "File not found")
    
    job = jobs[file_id]
    file_path = Path(job["file_path"])
    
    if not file_path.exists():
        raise HTTPException(404, "File not found on disk")
    
    try:
        # Extract using STEMMA's ingest module
        extraction = ingest.extract(file_path, ocr_max_pages=ocr_max_pages)
        
        # Build source candidate
        source_candidate = ingest.build_source_candidate(extraction, source_id=f"lhs:src.ingest-{file_id}")
        
        result = ExtractionResult(
            file_id=file_id,
            kind=extraction.kind,
            pages=extraction.pages,
            is_scanned=extraction.is_scanned,
            ocr_used=extraction.ocr_used,
            char_count=len(extraction.text),
            text_preview=extraction.text[:2000],
            source_candidate=source_candidate,
        )
        
        # Update job
        jobs[file_id].update({
            "status": "extracted",
            "extraction": {
                "kind": extraction.kind,
                "pages": extraction.pages,
                "is_scanned": extraction.is_scanned,
                "ocr_used": extraction.ocr_used,
                "text": extraction.text,
            },
            "source_candidate": source_candidate,
            "extracted_at": datetime.now(timezone.utc).isoformat(),
        })
        
        return result
        
    except ingest.IngestionError as e:
        raise HTTPException(500, f"Ingestion error: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Extraction failed: {str(e)}")

@app.post("/api/propose/{file_id}", response_model=ProposalResponse)
async def create_proposal(file_id: str, request: ProposalRequest):
    """Create a proposal from extracted content using STEMMA's curation pipeline."""
    if file_id not in jobs:
        raise HTTPException(404, "File not found")

    job = jobs[file_id]
    if job.get("status") != "extracted":
        raise HTTPException(400, "File must be extracted first")

    try:
        # Load extraction
        extraction_data = job["extraction"]
        extraction = ingest.Extraction(
            kind=extraction_data["kind"],
            text=extraction_data["text"],
            pages=extraction_data["pages"],
            is_scanned=extraction_data["is_scanned"],
            ocr_used=extraction_data["ocr_used"],
            source_name=Path(job["file_path"]).name,
        )

        # Create curation request
        request_obj = ingest.to_curation_request(extraction)
        request_obj.kind = request.kind

        # Determine draft callback (Deterministic vs LLM / Antigravity / Gemini)
        if request.use_llm:
            from ingestion_webapp.backend import llm_draft
            def custom_llm_draft(blueprint, data, **kw):
                return llm_draft.generate_llm_draft(
                    blueprint, data,
                    api_key=request.api_key,
                    model_name=request.model_name or "antigravity-gemini-3.7-flash",
                    provider=request.provider or "google",
                    **kw
                )
            draft_callback = custom_llm_draft
        elif request.draft_callback:
            module_name, func_name = request.draft_callback.split(":", 1)
            import importlib
            module = importlib.import_module(module_name)
            draft_callback = getattr(module, func_name)
        else:
            draft_callback = ingest_to_proposals._default_draft

        # Run curation pipeline
        decision = curation_pipeline.run_pipeline(
            request_obj,
            draft_callback=draft_callback,
            semantic_review_callback=lambda gate, artifact, bp: GateResult(gate, "pass", []),
        )

        # Build proposal dossier
        source_candidate = ingest.build_source_candidate(
            ingest.Extraction(**jobs[file_id]["extraction"], source_name=Path(job["file_path"]).name),
            source_id=f"lhs:src.ingest-{file_id}"
        )

        proposal_id = f"prop-{uuid.uuid4().hex[:8]}"
        dossier = {
            "schema_version": "0.1",
            "proposal_id": proposal_id,
            "submitter": request.submitter or job.get("submitter", "sajan"),
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "input_file": job["file_path"],
            "extraction": {
                "kind": extraction.kind,
                "pages": extraction.pages,
                "is_scanned": extraction.is_scanned,
                "ocr_used": extraction.ocr_used,
                "char_count": len(extraction.text),
            },
            "source_candidate": source_candidate,
            "proposal": {
                "decision": decision.action,
                "publishable": decision.publishable,
                "gates": [
                    {"gate": g.gate, "verdict": g.verdict, "findings": g.findings}
                    for g in decision.gates
                ],
                "artifact": decision.artifact,
                "reason": decision.reason,
            },
            "status": "proposed",
        }

        # Save proposal
        proposal_path = PROPOSALS_DIR / f"{proposal_id}.proposal.yaml"
        import yaml
        proposal_path.write_text(yaml.safe_dump(dossier, sort_keys=False, allow_unicode=True))

        # Update job
        jobs[file_id].update({
            "status": "proposed",
            "proposal_id": proposal_id,
            "proposal_path": str(proposal_path),
            "proposed_at": datetime.now(timezone.utc).isoformat(),
        })

        return ProposalResponse(
            proposal_id=proposal_id,
            file_id=file_id,
            status="proposed",
            decision=decision.action,
            publishable=decision.publishable,
            gates=[{"gate": g.gate, "verdict": g.verdict, "findings": g.findings} for g in decision.gates],
            artifact=decision.artifact,
            reason=decision.reason,
        )

    except Exception as e:
        raise HTTPException(500, f"Proposal creation failed: {str(e)}")

@app.get("/api/proposals", response_model=List[ProposalListItem])
async def list_proposals(status: Optional[str] = None):
    """List all proposals."""
    proposals = []
    for path in PROPOSALS_DIR.glob("*.proposal.yaml"):
        try:
            import yaml
            data = yaml.safe_load(path.read_text())
            if status and data.get("status") != status:
                continue
            proposals.append(ProposalListItem(
                proposal_id=data["proposal_id"],
                filename=data.get("input_file", "").split("/")[-1],
                created_at=data["created_at"],
                status=data["status"],
                decision=data["proposal"]["decision"],
                kind=data["proposal"]["artifact"].get("kind", "unknown") if data.get("proposal", {}).get("artifact") else "unknown",
                submitter=data.get("submitter", "sajan"),
            ))
        except Exception as e:
            print(f"Error loading proposal {path}: {e}")
    return proposals

@app.get("/api/proposals/{proposal_id}")
async def get_proposal(proposal_id: str):
    """Get full proposal details."""
    path = PROPOSALS_DIR / f"{proposal_id}.proposal.yaml"
    if not path.exists():
        raise HTTPException(404, "Proposal not found")
    import yaml
    return yaml.safe_load(path.read_text())

def check_review_permission(submitter: Optional[str], reviewer: str, reviewer_role: Optional[str] = None):
    submitter_clean = (submitter or "sajan").strip().lower()
    reviewer_clean = (reviewer or "").strip().lower()
    role_clean = (reviewer_role or "").strip().lower()
    
    is_self_review = (reviewer_clean == submitter_clean)
    is_admin_or_founder = role_clean in ["admin", "founder"] or reviewer_clean in ["sajan", "founder", "admin"]
    
    if is_self_review and not is_admin_or_founder:
        raise HTTPException(
            403,
            f"Submitter '{submitter}' cannot review their own proposal unless acting as Admin or Founder."
        )

@app.post("/api/proposals/{proposal_id}/review", response_model=ProposalResponse)
async def review_proposal(proposal_id: str, action: ReviewAction):
    """Human review action on a proposal."""
    path = PROPOSALS_DIR / f"{proposal_id}.proposal.yaml"
    if not path.exists():
        raise HTTPException(404, "Proposal not found")
    
    import yaml
    data = yaml.safe_load(path.read_text())
    
    # Check review permission (submitter self-review restriction unless admin/founder)
    submitter = data.get("submitter", "sajan")
    check_review_permission(submitter, action.reviewer, action.reviewer_role)
    
    # Load the connection/entity file if it exists
    artifact = data["proposal"].get("artifact")
    if not artifact:
        raise HTTPException(400, "No artifact in proposal")
    
    # Map review action to curation state transition
    from scripts import curation_state
    from scripts import review as review_script
    
    if action.action in ["accept", "reviewed"]:
        to_review = "reviewed"
    elif action.action == "canonicalize":
        to_review = "canonical"
    elif action.action == "reject":
        to_review = "rejected"
    else:
        raise HTTPException(400, f"Invalid action: {action.action}")
    
    # Apply transition to the artifact (if it's a connection)
    # This would need to be adapted based on artifact type
    # For now, update proposal status
    data["status"] = "reviewed" if action.action in ["accept", "reviewed"] else action.action
    data["reviewed_by"] = action.reviewer
    data["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    data["review_reason"] = action.reason
    
    # Save updated proposal
    import yaml
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
    
    return ProposalResponse(
        proposal_id=proposal_id,
        file_id=data.get("file_id", ""),
        status=data["status"],
        decision=data["proposal"]["decision"],
        publishable=data["proposal"]["publishable"],
        gates=data["proposal"]["gates"],
        artifact=data["proposal"].get("artifact"),
        reason=data["proposal"]["reason"],
    )

@app.post("/api/proposals/{proposal_id}/update", response_model=ProposalResponse)
async def update_proposal_artifact(proposal_id: str, request: ArtifactUpdateRequest):
    """Update proposal artifact fields and re-verify quality gates."""
    path = PROPOSALS_DIR / f"{proposal_id}.proposal.yaml"
    if not path.exists():
        raise HTTPException(404, "Proposal not found")

    import yaml
    data = yaml.safe_load(path.read_text())

    artifact = request.artifact
    data["proposal"]["artifact"] = artifact

    # Re-run quality gate checks with updated artifact
    try:
        extraction_data = data.get("extraction", {})
        extraction = ingest.Extraction(
            kind=extraction_data.get("kind", "document"),
            text="",
            pages=extraction_data.get("pages", 1),
            is_scanned=extraction_data.get("is_scanned", False),
            ocr_used=extraction_data.get("ocr_used", False),
            source_name=data.get("input_file", "").split("/")[-1],
        )
        request_obj = ingest.to_curation_request(extraction)
        request_obj.kind = artifact.get("type", "entity")
        blueprint = curation_pipeline.blueprint_from_request(request_obj)
        gates = curation_pipeline._run_deterministic_gates(request_obj, blueprint, artifact)
        decision = curation_pipeline.evaluate_gates(gates)

        data["proposal"]["gates"] = [
            {"gate": g.gate, "verdict": g.verdict, "findings": g.findings}
            for g in gates
        ]
        data["proposal"]["publishable"] = all(g.verdict == "pass" for g in gates)
        data["proposal"]["decision"] = decision.action
    except Exception as e:
        print(f"Gate verification re-run error: {e}")

    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    data["last_editor"] = request.editor or "sajan"

    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))

    return ProposalResponse(
        proposal_id=proposal_id,
        file_id=data.get("file_id", ""),
        status=data["status"],
        decision=data["proposal"]["decision"],
        publishable=data["proposal"]["publishable"],
        gates=data["proposal"]["gates"],
        artifact=data["proposal"].get("artifact"),
        reason=data["proposal"].get("reason", ""),
    )

@app.post("/api/canonicalize/{proposal_id}")
async def canonicalize_proposal(
    proposal_id: str, 
    reviewer: str = Form(...), 
    reviewer_role: Optional[str] = Form(default="founder"), 
    reason: Optional[str] = Form(default=None)
):
    """Canonicalize a proposal - move to canonical content."""
    path = PROPOSALS_DIR / f"{proposal_id}.proposal.yaml"
    if not path.exists():
        raise HTTPException(404, "Proposal not found")
    
    import yaml
    data = yaml.safe_load(path.read_text())
    
    submitter = data.get("submitter", "sajan")
    check_review_permission(submitter, reviewer, reviewer_role)
    
    artifact = data["proposal"].get("artifact", {})
    artifact_id = artifact.get("id", "")
    
    if not artifact_id or "<" in artifact_id or ">" in artifact_id:
        raise HTTPException(400, f"Invalid placeholder stable ID '{artifact_id}'. Please edit artifact ID to valid format (e.g. lhs:phys.newtons-second-law or lhs:conn.000001) before canonicalizing.")

    # Canonicalize artifact into content/ or sources/ or connections/
    if artifact_id.startswith("lhs:src."):
        source_file = ROOT / "sources" / f"{artifact_id}.yaml"
        source_file.write_text(yaml.safe_dump(artifact, sort_keys=False, allow_unicode=True))
    elif artifact_id.startswith("lhs:conn."):
        conn_file = ROOT / "connections" / f"{artifact_id}.yaml"
        conn_file.write_text(yaml.safe_dump(artifact, sort_keys=False, allow_unicode=True))
    else:
        # Entity markdown
        domain = artifact.get("domain", "general")
        domain_folder_map = {
            "physics": "physics/mechanics",
            "phys": "physics/mechanics",
            "chemistry": "chemistry/bonding-structure",
            "chem": "chemistry/bonding-structure",
            "biology": "biology/cell-biology",
            "bio": "biology/cell-biology",
            "math": "math/algebra",
            "earth-space": "earth-space",
            "engineering": "engineering",
            "scientific-practice": "scientific-practice"
        }
        subfolder = domain_folder_map.get(domain, "physics/mechanics")
        entity_dir = ROOT / "content" / subfolder
        entity_dir.mkdir(parents=True, exist_ok=True)
        
        slug = artifact_id.split(".")[-1]
        entity_file = entity_dir / f"{slug}.md"
        
        frontmatter = yaml.safe_dump(artifact, sort_keys=False, allow_unicode=True)
        content_text = f"---\n{frontmatter}---\n\n## Notes\n\nCanonicalized via STEMMA Ingestion Webapp.\n"
        entity_file.write_text(content_text)

    # Update proposal status
    data["status"] = "canonicalized"
    data["canonicalized_by"] = reviewer
    data["canonicalized_at"] = datetime.now(timezone.utc).isoformat()
    data["canonicalization_reason"] = reason
    
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
    
    # Regenerate exports
    subprocess.run([sys.executable, "scripts/validate.py"], cwd=ROOT)
    
    return {"status": "canonicalized", "proposal_id": proposal_id, "artifact_id": artifact_id}

@app.get("/api/jobs/{file_id}")
async def get_job_status(file_id: str):
    """Get job status."""
    if file_id not in jobs:
        raise HTTPException(404, "Job not found")
    return jobs[file_id]

@app.get("/api/files/{file_id}/download")
async def download_file(file_id: str):
    """Download original file."""
    if file_id not in jobs:
        raise HTTPException(404, "File not found")
    file_path = Path(jobs[file_id]["file_path"])
    if not file_path.exists():
        raise HTTPException(404, "File not found on disk")
    return FileResponse(file_path, filename=file_path.name)

@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str):
    """Delete uploaded file and associated data."""
    if file_id not in jobs:
        raise HTTPException(404, "File not found")
    
    job = jobs[file_id]
    # Delete files
    for path_key in ["file_path", "source_path", "proposal_path"]:
        if path_key in job:
            Path(job[path_key]).unlink(missing_ok=True)
    
    # Delete proposal if exists
    if "proposal_id" in job:
        proposal_path = PROPOSALS_DIR / f"{job['proposal_id']}.proposal.yaml"
        proposal_path.unlink(missing_ok=True)
    
    del jobs[file_id]
    return {"status": "deleted", "file_id": file_id}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)