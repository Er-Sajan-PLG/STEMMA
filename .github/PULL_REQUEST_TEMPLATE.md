## Summary

<!-- What changed and why. One paragraph. -->

## Gate checklist (must all pass before merge)

- [ ] `python3 scripts/verify_all.py` green
- [ ] `python3 -m pytest tests/ -q` green (full suite, no skips added)
- [ ] `python3 scripts/docs.py check` green (docs contract; run `docs sync` first and include the diff)
- [ ] If canonical content changed: HITL path used (human edit recorded in workflow/ audit) — never bypass `hitl_check`
- [ ] If export shape changed: `schema/VERSION.yaml` bumped via ADR, `docs/` updated, consumers considered

## Schema/contract impact

<!-- Any change to schema/, exports/, adapters/, relationship vocabulary, or
docs/ claims? Link the ADR or spec reference. -->

## Risk & rollback

<!-- What breaks if this is wrong; how to revert. -->
