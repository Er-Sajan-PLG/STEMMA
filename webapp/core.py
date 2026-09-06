#!/usr/bin/env python3
"""STEMMA ingestion/review webapp core.

A human-in-the-loop proposal-engineering layer. Every artifact lands under
``workflow/`` (git-ignored). Nothing in this module writes to content/,
connections/, or sources/ — the canonical tree is only *read* here, and the
only path to canonical is the existing human review flow
(``scripts/review.py`` + ``scripts/verify_all.py``).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import ingest  # noqa: E402
import validate  # noqa: E402

WORKFLOW_ENV = "STEMMA_WORKFLOW_DIR"
DEFAULT_WORKFLOW = ROOT / "workflow"

DOCUMENT_STATUSES = {"uploaded", "extracting", "ready", "error", "unsupported", "generated", "staged"}
KIND_LABEL = {"pdf": "PDF", "image": "Image (OCR)", "text": "Text file", "other": "Other/unsupported"}
SYSTEM_DRAFT_NOTE = "You produce only valid JSON proposal payloads for STEMMA."
DEFAULT_PROVIDERS = {
    "openai": {"base_url": "https://api.openai.com/v1", "model": "gpt-4o-mini"},
    "google": {"base_url": "https://generativelanguage.googleapis.com/v1beta", "model": "gemini-3-pro-preview"},
    # Local harnesses (Antigravity CLI/Gateway, DeepSeek harness, Cline/Continue
    # proxies, etc.) expose an OpenAI-compatible /v1/chat/completions endpoint.
    # Replace 127.0.0.1 with the harness machine/tunnel if the webapp is remote.
    "antigravity": {"base_url": "http://127.0.0.1:6012/v1", "model": "gemini-3-pro"},
}
SUPPORTED_PROVIDERS = tuple(DEFAULT_PROVIDERS)


class WebappError(ValueError):
    """Base error surfaced to the UI."""


class NotFound(WebappError):
    """Requested workflow object does not exist."""


class ProviderNotConfigured(WebappError):
    """No LLM provider is configured yet."""


class ProviderError(WebappError):
    """The configured provider returned an error."""


class ExtractionFailed(WebappError):
    """A document could not be extracted."""


class CandidateInvalid(WebappError):
    """A candidate failed the deterministic proposal checks."""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Workflow:
    """Owns the git-ignored workflow directory and its small JSONL state.

    The state is deliberately *not* canonical: it is a working area for a human
    to review upload -> extraction -> candidate -> staged-proposal.
    """

    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or Path(os.environ.get(WORKFLOW_ENV, DEFAULT_WORKFLOW))).resolve()
        self.uploads = self.root / "uploads"
        self.meta = self.root / "meta"
        self.extraction = self.root / "extraction"
        self.candidates = self.root / "candidates"
        self.proposals = self.root / "proposals"
        self.config = self.root / "config"
        self.audit = self.root / "audit"
        self.init_dirs()

    def init_dirs(self) -> None:
        for directory in (self.uploads, self.meta, self.extraction, self.candidates,
                          self.proposals, self.config, self.audit):
            directory.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    # Audit trail (human-readable append-only log)
    # ------------------------------------------------------------------ #
    def log(self, event: str, *, doc_id: str = "", detail: dict | None = None) -> None:
        entry = {
            "timestamp": now_iso(),
            "event": event,
            "doc_id": doc_id,
            "detail": detail or {},
        }
        with (self.audit / "audit.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")

    def read_audit(self, limit: int = 500) -> list[dict]:
        path = self.audit / "audit.jsonl"
        lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
        entries = []
        for line in lines[-limit:]:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                entries.append({"timestamp": "", "event": "unreadable", "detail": {"raw": line}})
        return entries

    # ------------------------------------------------------------------ #
    # LLM provider configuration (stored under git-ignored workflow/)
    # ------------------------------------------------------------------ #
    def read_llm_config(self, mask: bool = False) -> dict:
        path = self.config / "llm.json"
        if not path.exists():
            return {"provider": "antigravity", "base_url": "", "model": "", "api_key": "", "configured": False}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        key = data.get("api_key") or ""
        provider = data.get("provider") or "openai"
        out = {
            "provider": provider,
            "base_url": data.get("base_url") or "",
            "model": data.get("model") or "",
            "api_key": "••••" + key[-4:] if key and mask else key,
            "configured": bool(provider in SUPPORTED_PROVIDERS and data.get("base_url") and data.get("model") and key),
        }
        return out

    def save_llm_config(self, *, provider: str, base_url: str, model: str, api_key: str) -> dict:
        provider = (provider or "openai").strip().lower()
        if provider not in SUPPORTED_PROVIDERS:
            raise WebappError(
                "provider must be one of: " + ", ".join(SUPPORTED_PROVIDERS) +
                " (antigravity/openai use an OpenAI-compatible chat/completions harness)"
            )
        if not base_url or not model:
            raise WebappError("base_url and model are required to configure an LLM Draft")
        # The GET config masks the key. If the UI submitted the masked value
        # (the user did not type a new key), preserve the existing secret.
        existing = self.read_llm_config()
        if existing.get("provider") != provider:
            # Switching providers always requires a fresh key (no cross-provider secret reuse).
            existing = {"api_key": ""}
        if api_key.startswith("••••") or not api_key.strip():
            api_key = existing.get("api_key") or ""
        data = {
            "provider": provider,
            "base_url": base_url.strip().rstrip("/"),
            "model": model.strip(),
            "api_key": api_key.strip(),
        }
        (self.config / "llm.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        self.log("config_saved", detail={"base_url": data["base_url"], "model": data["model"]})
        return self.read_llm_config(mask=True)

    # ------------------------------------------------------------------ #
    # Upload + extraction
    # ------------------------------------------------------------------ #
    def accept_upload(self, *, original_name: str, mime: str, data: bytes) -> dict:
        if not original_name or not data:
            raise WebappError("upload requires a non-empty filename and content")
        doc_id = uuid.uuid4().hex[:16]
        safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", Path(original_name).name)
        stored = self.uploads / f"{doc_id}_{safe_name}"
        stored.write_bytes(data)
        suffix = Path(original_name).suffix.lower() or ".bin"
        try:
            kind = ingest.detect_kind(Path(original_name))
        except ingest.IngestionError:
            kind = "other"
        record = {
            "id": doc_id,
            "original_name": original_name,
            "stored_name": safe_name,
            "stored_path": str(stored.relative_to(self.root)),
            "suffix": suffix,
            "mime": mime,
            "size_bytes": len(data),
            "kind": kind,
            "status": "uploaded",
            "error": None,
            "extraction": None,
            "created_at": now_iso(),
            "updated_at": now_iso(),
        }
        self._write_meta(record)
        self.log("document_uploaded", doc_id=doc_id,
                  detail={"name": original_name, "size": len(data), "kind": kind})
        return record

    def test_llm_provider(self) -> dict:
        """Send a tiny probe to the configured provider (no document/draft)."""
        config = self.read_llm_config()
        if not config["configured"]:
            raise ProviderNotConfigured(
                "No LLM Draft provider configured. Open Settings, pick a provider "
                "(Google Gemini / OpenAI-compatible), enter base URL, model, API key, then retry."
            )
        try:
            payload = self._llm_chat(config, 'Return ONLY this JSON object: {"candidates": []}')
        except ProviderError as exc:
            return {"ok": False, "provider": config.get("provider"), "error": str(exc)}
        return {"ok": True, "provider": config.get("provider"), "model": config.get("model"),
                "keys": sorted((payload or {}).keys())[:8]}

    def list_documents(self) -> list[dict]:
        records = [self._read_meta(path) for path in sorted(self.meta.glob("*.json"))]
        return [r for r in records if r]

    def get_document(self, doc_id: str) -> dict:
        record = self._read_meta(self._meta_path(doc_id))
        if record is None:
            raise NotFound(f"document not found: {doc_id}")
        return record

    def _metadata_for_doc(self, doc_id: str) -> dict:
        record = self.get_document(doc_id)
        return {
            "id": record["id"],
            "original_name": record["original_name"],
            "stored_path": record["stored_path"],
            "kind": record["kind"],
            "status": record["status"],
            "extraction": record.get("extraction") or {},
        }

    def extract_document(self, doc_id: str) -> dict:
        record = self.get_document(doc_id)
        record["status"] = "extracting"
        record["updated_at"] = now_iso()
        self._write_meta(record)
        self.log("extraction_started", doc_id=doc_id)
        stored = self.root / record["stored_path"]
        kind = record.get("kind") or "other"
        try:
            kind = ingest.detect_kind(Path(record["original_name"]))
            if kind == "other":
                raise ingest.IngestionError(
                    f"unsupported document type '{record['suffix']}'. The file is "
                    "retained for manual review; add an extractor or convert it "
                    "to PDF/text and upload again."
                )
            ex = ingest.extract(stored)
        except ingest.IngestionError as exc:
            failed_kind = "other" if "unsupported document type" in str(exc) or "unsupported" in str(exc) else kind
            record["status"] = "error" if failed_kind != "other" else "unsupported"
            record["error"] = str(exc)
            record["extraction"] = {"kind": "other", "status": "failed", "reason": str(exc)}
            record["updated_at"] = now_iso()
            self._write_meta(record)
            self.log("extraction_error", doc_id=doc_id, detail={"reason": str(exc)})
            return record

        text_path = self.extraction / f"{doc_id}.txt"
        text_path.write_text(ex.text, encoding="utf-8")
        sidecar = ingest.build_extraction_sidecar(ex)
        record["kind"] = ex.kind
        record["status"] = "ready"
        record["error"] = None
        record["extraction"] = sidecar
        record["extraction"]["status"] = "ready"
        record["extraction"]["text_path"] = str(text_path.relative_to(self.root))
        record["extraction"]["char_count"] = len(ex.text)
        record["updated_at"] = now_iso()
        self._write_meta(record)
        self.log("extraction_complete", doc_id=doc_id,
                  detail={"kind": ex.kind, "chars": len(ex.text), "ocr": ex.ocr_used})
        return record

    # ------------------------------------------------------------------ #
    # Candidate generation via the configured LLM Draft seam
    # ------------------------------------------------------------------ #
    def generate_candidates(self, doc_id: str, *, target_kinds: list[str] | None = None) -> dict:
        record = self.get_document(doc_id)
        if record.get("status") == "error":
            raise ExtractionFailed(f"document has an extraction error: {record['error']}")
        if record.get("status") == "uploaded" or not record.get("extraction"):
            record = self.extract_document(doc_id)
        if record.get("status") == "unsupported":
            raise ExtractionFailed("document type is unsupported and cannot be drafted")
        config = self.read_llm_config()
        if not config["configured"]:
            raise ProviderNotConfigured(
                "No LLM Draft provider configured. Open Settings, provide base_url, "
                "model, and API key, then retry. No content is generated until then."
            )
        text = (self.extraction / f"{doc_id}.txt").read_text(encoding="utf-8")
        known_ids = self._known_entity_ids()
        targets = target_kinds or ["entity", "connection"]
        prompt = self._draft_prompt(record, text, known_ids, targets)
        payload = self._llm_chat(config, prompt)
        candidates = self._parse_candidate_payload(payload, doc_id)
        for candidate in candidates:
            findings = self.validate_candidate(candidate["kind"], candidate["proposal"])
            candidate["findings"] = findings
        out = {"doc_id": doc_id, "generated_at": now_iso(), "candidates": candidates}
        (self.candidates / f"{doc_id}.json").write_text(
            json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        record["status"] = "generated"
        record["updated_at"] = now_iso()
        self._write_meta(record)
        self.log("candidates_generated", doc_id=doc_id, detail={"count": len(candidates)})
        return out

    def list_candidates(self, doc_id: str | None = None) -> list[dict]:
        if doc_id:
            return self._candidate_file(doc_id).get("candidates", [])
        out = []
        for path in sorted(self.candidates.glob("*.json")):
            out.extend(self._read_json(path).get("candidates", []))
        return out

    def update_candidate(self, candidate_id: str, *, proposal: dict) -> dict:
        for path in self.candidates.glob("*.json"):
            data = self._read_json(path)
            for candidate in data["candidates"]:
                if candidate["id"] == candidate_id:
                    candidate["proposal"] = proposal
                    candidate["findings"] = self.validate_candidate(candidate["kind"], proposal)
                    candidate["updated_at"] = now_iso()
                    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                    self.log("candidate_edited", doc_id=data.get("doc_id", ""),
                             detail={"candidate_id": candidate_id})
                    return candidate
        raise NotFound(f"candidate not found: {candidate_id}")

    def delete_candidate(self, candidate_id: str) -> None:
        for path in self.candidates.glob("*.json"):
            data = self._read_json(path)
            before = len(data.get("candidates", []))
            data["candidates"] = [c for c in data.get("candidates", []) if c["id"] != candidate_id]
            if len(data["candidates"]) != before:
                path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
                self.log("candidate_deleted", doc_id=data.get("doc_id", ""), detail={"candidate_id": candidate_id})
                return
        raise NotFound(f"candidate not found: {candidate_id}")

    def stage_candidate(self, candidate_id: str, *, reviewer: str, note: str = "") -> dict:
        candidate = self._find_candidate(candidate_id)
        findings = self.validate_candidate(candidate["kind"], candidate["proposal"])
        if findings:
            raise CandidateInvalid(
                f"candidate has deterministic findings and is not stage-ready: {findings[:5]}"
            )
        doc = self.get_document(candidate["doc_id"])
        proposal = candidate["proposal"]
        slug = self._proposal_slug(proposal)
        record = {
            "workflow_status": "proposed",
            "schema_version": "1.1.0",
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "kind": candidate["kind"],
            "source_document": self._metadata_for_doc(candidate["doc_id"]),
            "source_candidate": self._source_candidate_for(doc),
            "candidate": proposal,
            "human_review": {"reviewer": reviewer, "note": note, "at": now_iso()},
            "provenance": {"origin": f"webapp-human-review:{reviewer}", "generated_by": "webapp"},
            "destination": {
                "canonical": "content/ | connections/ | sources/",
                "note": "NOT written by this app. A human must verify and run "
                        "scripts/review.py + scripts/verify_all.py before any canonical change.",
            },
        }
        path = self.proposals / f"{slug}.{candidate['kind']}.proposal.yaml"
        self._write_yaml(path, record)
        doc["status"] = "staged"
        doc["updated_at"] = now_iso()
        self._write_meta(doc)
        self.log("proposal_staged", doc_id=candidate["doc_id"],
                  detail={"candidate_id": candidate_id, "path": str(path.relative_to(self.root))})
        return {"path": str(path.relative_to(self.root)), "record": record}

    def list_proposals(self) -> list[dict]:
        out = []
        for path in sorted(self.proposals.glob("*.yaml")):
            out.append({"path": str(path.relative_to(self.root)), "record": self._read_yaml(path)})
        return out

    # ------------------------------------------------------------------ #
    # Validation + provider helpers
    # ------------------------------------------------------------------ #
    def validate_candidate(self, kind: str, data: dict) -> list[str]:
        errs: list[str] = []
        if kind == "entity":
            slug = str(data.get("id", "")).rsplit(".", 1)[-1]
            data = {**data, "_file": f"<proposed:{data.get('id', 'new')}>"}
            validate.validate_entity(data, errs, filename_slug=slug)
            try:
                domain_map = validate.load_id_domain_map()
                vocab = (validate.load_vocabulary(validate.VOCAB_DOMAINS) or {}).get("domains") or []
                validate.check_entity_domain_identity(data, domain_map, vocab, errs)
            except Exception as exc:  # pragma: no cover - defensive
                errs.append(f"domain-identity check unavailable: {exc}")
        elif kind == "connection":
            entities = self._known_ids_by_type()
            sources = {}
            data = {**data, "_file": f"<proposed:{data.get('id', 'new')}>"}
            validate.validate_connection(data, entities, sources, errs)
        else:
            errs.append(f"unknown candidate kind: {kind}")
        return errs

    def _draft_prompt(self, doc: dict, text: str, known_ids: list[str], targets: list[str]) -> str:
        relation_names = sorted(
            (validate.load_relation_registry().get("relations") or {}).keys()
        )
        target_md = ", ".join(targets)
        return (
            "You are the STEMMA Draft seam. Produce schema-shaped PROPOSALS for a human "
            "reviewer; you never write to canonical knowledge.\n\n"
            f"Target object kinds: {target_md}.\n"
            "Entity proposal shape: id=stemma:<domain>.<slug> (domain from vocab: "
            "physics, chemistry, biology, earth-space, engineering, mathematics, "
            "scientific-practice), type=concept|quantity|law|unit|equation|phenomenon|model|experiment, "
            "name, domain, status=draft, definition, provenance={ai_drafted:false, source: <source_id>}.\n"
            "Connection proposal shape: id=stemma:conn.000000 (placeholder; a human will assign the "
            "real immutable id), type=connection, source/target must be an existing entity id from the "
            "known_id list (below), relation must be one of the valid relations, "
            "assertion={status:active,type:proposed,review:{status:unreviewed}}, "
            "provenance={asserted_by,generated_by,method}.\n"
            f"Valid relations: {', '.join(relation_names)}.\n"
            f"Known entity IDs (exact strings only): {', '.join(sorted(known_ids))}\n"
            f"Source document: {doc['original_name']} ({doc.get('kind')}).\n"
            "Return ONLY JSON: {\"candidates\":[{\"kind\":\"entity\",\"proposal\":{...}}, ...]}.\n\n"
            f"EXTRACTED TEXT:\n{text[:12000]}"
        )

    @staticmethod
    def _openai_request(config: dict, prompt: str) -> tuple[str, bytes, dict[str, str]]:
        url = f"{config['base_url']}/chat/completions"
        body = {
            "model": config["model"],
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": SYSTEM_DRAFT_NOTE},
                {"role": "user", "content": prompt},
            ],
        }
        # Official OpenAI supports response_format json_object; many local
        # harnesses (Antigravity CLI/Gateway, DeepSeek harness, Continue etc.)
        # reject it, so only send it for the canonical OpenAI provider. The
        # parser strips markdown fences as a safety net either way.
        if config.get("provider") == "openai":
            body["response_format"] = {"type": "json_object"}
        return url, json.dumps(body).encode("utf-8"), {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['api_key']}",
        }

    @staticmethod
    def _google_request(config: dict, prompt: str) -> tuple[str, bytes, dict[str, str]]:
        # Gemini REST (Google AI Studio / GenAI Developer API, and the Gemini API
        # backing Antigravity-style agents): POST /models/{model}:generateContent
        # with x-goog-api-key and a generationConfig responseMimeType of json.
        url = f"{config['base_url']}/models/{config['model']}:generateContent"
        body = json.dumps({
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "systemInstruction": {
                "parts": [{"text": f"{SYSTEM_DRAFT_NOTE} Return only a JSON object; no markdown fences."}]
            },
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json",
            },
        }).encode("utf-8")
        headers = {"Content-Type": "application/json", "x-goog-api-key": config["api_key"]}
        return url, body, headers

    @staticmethod
    def _parse_google_payload(payload: dict) -> dict:
        parts = (
            payload.get("candidates") or [{}]
        )[0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts if isinstance(p, dict)).strip()
        if not text:
            raise ProviderError(f"Google model returned no text: {json.dumps(payload)[:300]}")
        # Google may wrap JSON in ```json ... ``` fences despite responseMimeType.
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        try:
            return json.loads(text) if isinstance(text, str) else text
        except json.JSONDecodeError as exc:
            raise ProviderError(f"Google model returned non-JSON content: {text[:300]}") from exc

    @staticmethod
    def _parse_openai_payload(payload: dict) -> dict:
        content = payload["choices"][0]["message"]["content"]
        if isinstance(content, str):
            text = content.strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*", "", text)
                text = re.sub(r"\s*```$", "", text)
            return json.loads(text)
        return content

    def _llm_chat(self, config: dict, prompt: str) -> dict:
        import urllib.error
        import urllib.request

        provider = config.get("provider") or "openai"
        if provider == "google":
            url, body, headers = self._google_request(config, prompt)
            parse = self._parse_google_payload
        else:
            url, body, headers = self._openai_request(config, prompt)
            parse = self._parse_openai_payload

        request = urllib.request.Request(url, data=body, method="POST")
        for key, value in headers.items():
            request.add_header(key, value)
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            raise ProviderError(f"LLM provider returned HTTP {exc.code}: {exc.read().decode('utf-8')[:300]}") from exc
        except Exception as exc:  # noqa: BLE001
            raise ProviderError(f"LLM provider request failed: {exc}") from exc
        try:
            return parse(json.loads(raw))
        except ProviderError:
            raise
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise ProviderError(f"LLM provider returned an unexpected payload: {raw[:300]}") from exc

    def _parse_candidate_payload(self, payload: dict, doc_id: str) -> list[dict]:
        candidates = []
        for index, item in enumerate(payload.get("candidates") or []):
            kind = item.get("kind")
            proposal = item.get("proposal")
            if kind not in {"entity", "connection"} or not isinstance(proposal, dict):
                raise ProviderError(f"candidate {index} is not a valid {kind}/proposal pair")
            candidates.append({
                "id": uuid.uuid4().hex[:12],
                "doc_id": doc_id,
                "kind": kind,
                "proposal": proposal,
                "findings": [],
                "created_at": now_iso(),
                "updated_at": now_iso(),
            })
        if not candidates:
            raise ProviderError("LLM returned no candidates")
        return candidates

    # ------------------------------------------------------------------ #
    # Known canonical IDs (read-only)
    # ------------------------------------------------------------------ #
    def _known_entity_ids(self) -> list[str]:
        ids = []
        for path in sorted((ROOT / "content").rglob("*.md")):
            if path.read_text(encoding="utf-8").startswith("---"):
                try:
                    data = validate.parse_entity(path)
                except ValueError:
                    continue
                if isinstance(data.get("id"), str):
                    ids.append(data["id"])
        return ids

    def _known_ids_by_type(self) -> dict[str, dict]:
        out = {}
        for path in sorted((ROOT / "content").rglob("*.md")):
            if path.read_text(encoding="utf-8").startswith("---"):
                try:
                    data = validate.parse_entity(path)
                except ValueError:
                    continue
                if isinstance(data.get("id"), str):
                    out[data["id"]] = data
        return out

    def _source_candidate_for(self, doc: dict) -> dict:
        return {
            "id": f"stemma:src.webapp-{doc['id']}",
            "type": "other",
            "citation": f"Webapp-uploaded document: {doc['original_name']}",
            "title": doc["original_name"],
        }

    @staticmethod
    def _proposal_slug(proposal: dict) -> str:
        _id = str(proposal.get("id") or "proposal")
        return re.sub(r"[^a-zA-Z0-9._-]", "-", _id.split(":", 1)[-1]).strip("-") or "proposal"

    # ------------------------------------------------------------------ #
    # Persistence helpers
    # ------------------------------------------------------------------ #
    def _meta_path(self, doc_id: str) -> Path:
        if not re.fullmatch(r"[a-f0-9]{16}", doc_id):
            raise NotFound(f"invalid document id: {doc_id}")
        return self.meta / f"{doc_id}.json"

    def _read_meta(self, path: Path) -> dict | None:
        data = self._read_json(path)
        if isinstance(data, dict) and data.get("id"):
            return data
        return None

    def _write_meta(self, record: dict) -> None:
        (self.meta / f"{record['id']}.json").write_text(
            json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    def _candidate_file(self, doc_id: str) -> dict:
        path = self.candidates / f"{doc_id}.json"
        if not path.exists():
            return {"doc_id": doc_id, "generated_at": now_iso(), "candidates": []}
        return self._read_json(path)

    def _find_candidate(self, candidate_id: str) -> dict:
        for path in self.candidates.glob("*.json"):
            data = self._read_json(path)
            for candidate in data.get("candidates", []):
                if candidate["id"] == candidate_id:
                    return candidate
        raise NotFound(f"candidate not found: {candidate_id}")

    @staticmethod
    def _read_json(path: Path) -> dict:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def _write_yaml(path: Path, record: dict) -> None:
        import yaml

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            yaml.safe_dump(record, sort_keys=False, allow_unicode=True), encoding="utf-8"
        )

    @staticmethod
    def _read_yaml(path: Path) -> dict:
        import yaml

        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
