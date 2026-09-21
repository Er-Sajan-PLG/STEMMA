# IFACE-STEMMA-GATE-001 — verification chain CLI contract

| Field | Value |
|---|---|
| ID | IFACE-STEMMA-GATE-001 |
| Provider | `scripts/verify_all.py` (and individual gate steps) |
| Consumers | curators, agents, pre-commit hook, GitHub Actions CI, Makefile targets |
| Owner | Sajan (SOLE_OWNER) |
| Purpose | Single authoritative command deciding "does the repository ship" |
| Version | unversioned CLI; behavioral contract pinned by this record + CI usage |
| Schema/Contract | exit code semantics + stdout `OK/FAIL/INFO` line conventions |
| Inputs | working tree; interpreter with `requirements.txt` installed |
| Outputs | exit 0 = valid; non-zero = fail-closed on first failing step; stdout per-step `OK:` lines; derived checks printed as `INFO:` (non-fatal by design — EVID-STEMMA-GATE-010) |
| Errors | exits: 0 success; non-zero from subprocess step (e.g., 1 validation failure, 2 missing dependency) |
| AuthN/AuthZ | Local execution; CI context inherits repo permissions (read-only contents) |
| Compatibility policy | Adding FAIL-level steps is a contract change (tightening); consumers (pre-commit) must tolerate full-chain runtime |
| Deprecation policy | Steps are removed only via ADR-level decision (observed convention) |
| Migration path | N/A |
| Related requirements | REQ-STEMMA-GATE-001..005; REQ-STEMMA-OPS-001 |
| Related verification | EVID-STEMMA-GATE-001/-002 (observed behavior), CI job definitions (inspection) |
