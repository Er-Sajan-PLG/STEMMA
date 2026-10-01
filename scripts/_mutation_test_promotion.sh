#!/usr/bin/env bash
# Mutation tests for the ADR-0057 / ENF-STEMMA-HITL-001..004 promotion + debt gate.
# Each case injects ONE violation, asserts validate.py exits non-zero, restores.
#
# Updated 2026-10-01 for two owner rulings:
#   * board waiver active  (ENF-003 board_waiver) — chain is validator -> independent_validator
#   * debt blocks fully    (ENF-002 pilot_scale_block, block_mode=full)
set -u
cd "$(dirname "$0")/.."
PY=.venv/bin/python
M=content/physics/measurement-units/metre.md
C=connections/conn.000156.yaml
cp "$M" /tmp/m.bak; cp "$C" /tmp/c.bak
fail=0

check() { # name, expected_exit
  $PY scripts/validate.py >/tmp/out.txt 2>&1
  local got=$?
  if [ "$got" -ne "$2" ]; then echo "FAIL [$1]: expected exit $2 got $got"; sed -n '1,4p' /tmp/out.txt; fail=1
  else echo "ok   [$1]: exit $got"; fi
}

restore() { cp /tmp/m.bak "$M"; cp /tmp/c.bak "$C"; }

echo "--- baseline ---"; check baseline 0; restore

echo "--- M1: same-day stages (breaks >=1 day rule) ---"
$PY - <<'PY'
import pathlib
p=pathlib.Path("content/physics/measurement-units/metre.md"); t=p.read_text()
t=t.replace("2026-09-24T09:10:00+00:00","2026-09-23T09:10:00+00:00",1)
p.write_text(t)
PY
check M1_same_day 1; restore

echo "--- M2: drop independent stage (incomplete waived chain) ---"
$PY - <<'PY'
import yaml,pathlib
p=pathlib.Path("content/physics/measurement-units/metre.md"); raw=p.read_text(); fm,body=raw.split("---",2)[1],raw.split("---",2)[2]
d=yaml.safe_load(fm); d["provenance"]["promotion_history"]=d["provenance"]["promotion_history"][:1]
p.write_text("---\n"+yaml.safe_dump(d,sort_keys=False,allow_unicode=True)+"---\n"+body.lstrip("\n"))
PY
check M2_missing_independent 1; restore

echo "--- M3: append a board stage while the board is waived ---"
$PY - <<'PY'
import yaml,pathlib
p=pathlib.Path("content/physics/measurement-units/metre.md"); raw=p.read_text(); fm,body=raw.split("---",2)[1],raw.split("---",2)[2]
d=yaml.safe_load(fm)
d["provenance"]["promotion_history"].append({"stage":"board","actor":"human:curator.001","at":"2026-09-25T11:00:00+00:00","board_members":["human:curator.001"],"independence_waiver":{"sanctioned_by":"human:curator.001","reason":"x","retire_when":"y"}})
p.write_text("---\n"+yaml.safe_dump(d,sort_keys=False,allow_unicode=True)+"---\n"+body.lstrip("\n"))
PY
check M3_board_while_waived 1; restore

echo "--- M4: canonical with empty promotion_history ---"
$PY - <<'PY'
import yaml,pathlib
p=pathlib.Path("content/physics/measurement-units/metre.md"); raw=p.read_text(); fm,body=raw.split("---",2)[1],raw.split("---",2)[2]
d=yaml.safe_load(fm); d["provenance"]["promotion_history"]=[]
p.write_text("---\n"+yaml.safe_dump(d,sort_keys=False,allow_unicode=True)+"---\n"+body.lstrip("\n"))
PY
check M4_empty_history 1; restore

echo "--- M5: outstanding debt on a reviewed record (FULL block) ---"
$PY - <<'PY'
import yaml,pathlib
p=pathlib.Path("content/physics/measurement-units/metre.md"); raw=p.read_text(); fm,body=raw.split("---",2)[1],raw.split("---",2)[2]
d=yaml.safe_load(fm)
d["revalidation_debt"]={"status":"outstanding","reason":"connection_obligations_pending","incurred_at":"2026-10-01","items":[]}
p.write_text("---\n"+yaml.safe_dump(d,sort_keys=False,allow_unicode=True)+"---\n"+body.lstrip("\n"))
PY
check M5_debt_full_block 1; restore

echo "--- M6: connection canonical with empty history ---"
$PY - <<'PY'
import yaml,pathlib
p=pathlib.Path("connections/conn.000156.yaml"); d=yaml.safe_load(p.read_text())
d["provenance"]["promotion_history"]=[]
p.write_text(yaml.safe_dump(d,sort_keys=False,allow_unicode=True))
PY
check M6_conn_no_history 1; restore

echo "--- M7: connection with outstanding debt (all datasets) ---"
$PY - <<'PY'
import yaml,pathlib
p=pathlib.Path("connections/conn.000156.yaml"); d=yaml.safe_load(p.read_text())
d["revalidation_debt"]={"status":"outstanding","reason":"endpoint_revalidated","incurred_at":"2026-10-01","items":[]}
p.write_text(yaml.safe_dump(d,sort_keys=False,allow_unicode=True))
PY
check M7_conn_debt 1; restore

echo "--- M8: deleting the enforcement registry (fail closed) ---"
mv spec/machine-readable/enforcement_rules.yaml /tmp/enf.bak
check M8_no_registry 1
mv /tmp/enf.bak spec/machine-readable/enforcement_rules.yaml; restore

echo "--- restore + final baseline ---"; restore; check restored 0

if [ "$fail" -eq 0 ]; then echo "ALL MUTATIONS BEHAVED"; else echo "MUTATION SUITE FAILED"; fi
exit $fail
