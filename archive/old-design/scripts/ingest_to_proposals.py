#!/usr/bin/env python3
"""STEMMA (`stemma:` namespace) ingestion → proposal staging runner.

Ties the pipeline together: ingest a document (PDF/image/scanned) and stage
review-ready candidate knowledge (source + proposed entities/connections) under
``proposals/`` — never under canonical ``content/``/``connections/``/``sources/``.

Flow:
    ingest.extract(doc)  →  to_curation_request()  →  curation_pipeline.run_pipeline()
      (extract text)          (propose candidate)         (hard-gate decision)

A real runner plugs an LLM Draft seam in via --draft (a module:function). Without
one, the built-in deterministic seam produces a Source candidate + a clearly-marked
placeholder proposal for human/LLM completion. In every case the output is a
PROPOSAL for the human Governance Gate — nothing automatically becomes canonical.

Usage:
    python3 scripts/ingest_to_proposals.py --path doc.pdf
    python3 scripts/ingest_to_proposals.py --path scan.pdf --json
    python3 scripts/ingest_to_proposals.py --path img.png \
        --draft mymodule:my_draft_fn            # LLM seam example
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import curation_pipeline
import ingest


class DraftSeamError(ValueError):
    """No real Draft seam is wired. Refuse to stage a placeholder proposal."""


class ProposalGateError(ValueError):
    """A staged proposal failed the deterministic curation gates; refusing to write."""


def _default_draft(blueprint: "Any", data: dict, **kw: Any) -> dict:
    """Dead-simple fallback that FAILS CLOSED (ADR-0035).

    A runner must supply a real LLM/rule Draft via `--draft module:function`.
    The only object we can deterministically stage without a seam is the Source
    candidate itself; an entity/connection placeholder is not schema-valid and
    would contaminate the proposal queue, so we refuse.
    """
    if blueprint.kind == "source":
        return data  # source is schema-valid and needs no LLM draft
    raise DraftSeamError(
        "no real Draft seam wired: refusing to stage a non-schema-valid placeholder. "
        "Pass --draft 'module:function' after providing a real Draft callback."
    )


def _load_seam(spec: str) -> Any:
    mod, _, fn = spec.partition(":")
    if not mod or not fn:
        raise SystemExit("--draft must be 'module:function'")
    import importlib
    return getattr(importlib.import_module(mod), fn)


def stage(doc: Path, *, draft: Any = None, ocr_max_pages: int = ingest._MAX_OCR_PAGES) -> dict:
    """Ingest a document and stage a proposal dossier under proposals/.

    ADR-0035: without a real Draft seam this refuses to stage (fail closed). With
    a seam, the deterministic curation gates must pass before a dossier is
    returned/written; a failing candidate is never silently staged.
    """
    if draft is None:
        raise DraftSeamError(
            "no real Draft seam wired: refusing to stage a non-schema-valid placeholder. "
            "Pass --draft 'module:function' after providing a real Draft callback."
        )
    ex = ingest.extract(doc, ocr_max_pages=ocr_max_pages)
    request = ingest.to_curation_request(ex)
    decision = curation_pipeline.run_pipeline(
        request,
        draft_callback=draft,
        semantic_review_callback=lambda gate, artifact, bp: curation_pipeline.GateResult(
            gate, "pass", []
        ),
    )
    if not decision.publishable:
        failed = [
            {"gate": g.gate, "findings": g.findings}
            for g in decision.gates
            if g.verdict == "fail"
        ]
        raise ProposalGateError(
            f"proposal failed the curation gate; refusing to stage: {failed} "
            f"(decision: {decision.action} — fix the draft or its source)."
        )

    source = ingest.build_source_candidate(ex)
    dossier = {
        "schema_version": "0.1",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "input_file": str(doc),
        "extraction": {
            "kind": ex.kind,
            "pages": ex.pages,
            "is_scanned": ex.is_scanned,
            "ocr_used": ex.ocr_used,
            "char_count": len(ex.text),
        },
        "source_candidate": source,
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
        "status": "proposed",  # NEVER canonical; human must approve
    }
    return dossier


def write_dossier(dossier: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = dossier["source_candidate"]["id"].split(".")[-1]
    path = out_dir / f"{slug}.proposal.yaml"
    # Strip extracted full text (huge) to keep the proposal readable; keep preview.
    body = {**dossier, "extraction": {**dossier["extraction"]}}
    body["source_candidate"] = {k: v for k, v in dossier["source_candidate"].items() if k != "extracted_text_preview"}
    path.write_text(yaml.safe_dump(body, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser(description="Ingest a document and stage STEMMA proposals for review.")
    p.add_argument("--path", required=True, help="PDF/image file to ingest")
    p.add_argument("--draft", default=None, help="'module:function' LLM Draft seam (optional)")
    p.add_argument("--out", default=str(ROOT / "proposals"), help="proposal staging dir")
    p.add_argument("--json", action="store_true", help="emit dossier as JSON to stdout")
    args = p.parse_args(argv)

    doc = Path(args.path).resolve()
    try:
        if not args.draft:
            raise DraftSeamError(
                "no real Draft seam wired: refusing to stage a non-schema-valid "
                "placeholder. Pass --draft 'module:function' after providing a "
                "real Draft callback."
            )
        draft = _load_seam(args.draft)
        dossier = stage(doc, draft=draft)
    except (ingest.IngestionError, DraftSeamError, ProposalGateError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(dossier, indent=2, default=str))
        return 0

    out = write_dossier(dossier, Path(args.out))
    print(f"ingested: {doc.name} ({dossier['extraction']['kind']}, "
          f"{dossier['extraction']['pages']} pages, "
          f"{'OCR' if dossier['extraction']['ocr_used'] else 'text'}, "
          f"{dossier['extraction']['char_count']} chars)")
    print(f"decision: {dossier['proposal']['decision']} (publishable={dossier['proposal']['publishable']})")
    print(f"proposal staged: {out}")
    print("NOTE: this is a PROPOSAL for human review — it is NOT canonical and was NOT "
          "written to content/, connections/, or sources/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())