#!/usr/bin/env bash
# Mutation tests for the ADR-0057 / ENF-STEMMA-HITL-001..004 promotion + debt gate.
# Each case injects ONE violation, asserts validate.py exits non-zero, restores.
set -u
cd "$(dirname "$0")/.."
M=content/physics/measurement-units/metre.md
C=connections/conn.000156.yaml
cp "$M" /tmp/m.bak; cp "$C" /tmp/c.bak
fail=0

check() { # name, expected_exit
  python3 scripts/validate.py >/tmp/out.txt 2>&1
  local got=$?
  if [ "$got" -ne "$2" ]; then echo "FAIL [$1]: expected exit $2 got $got"; sed -n '1,4p' /tmp/out.txt; fail=1
  else echo "ok   [$1]: exit $got"; fi
}

restore() { cp /tmp/m.bak "$M"; cp /tmp/c.bak "$C"; }

echo "--- baseline ---"; check baseline 0; restore

echo "--- M1: same-day stages (breaks >=1 day rule) ---"
python3 - <<'PY'
import re,pathlib
p=pathlib.Path("content/physics/measurement-units/metre.md"); t=p.read_text()
t=t.replace("2026-09-24T09:10:00+00:00","2026-09-23T09:10:00+00:00",1)
p.write_text(t)
PY
check M1_same_day 1; restore

echo "--- M2: drop board stage (incomplete chain) ---"
python3 - <<'PY'
import yaml,pathlib
p=pathlib.Path("content/physics/measurement-units/metre.md"); raw=p.read_text(); fm,body=raw.split("---",2)[1],raw.split("---",2)[2]
d=yaml.safe_load(fm); d["provenance"]["promotion_history"]=d["provenance"]["promotion_history"][:2]
p.write_text("---\n"+yaml.safe_dump(d,sort_keys=False,allow_unicode=True)+"---\n"+body.lstrip("\n"))
PY
check M2_missing_board 1; restore

echo "--- M3: board under 2 humans w/o waiver (remove waiver from board entry) ---"
python3 - <<'PY'
import yaml,pathlib
p=pathlib.Path("content/physics/measurement-units/metre.md"); raw=p.read_text(); fm,body=raw.split("---",2)[1],raw.split("---",2)[2]
d=yaml.safe_load(fm); d["provenance"]["promotion_history"][2].pop("independence_waiver",None)
p.write_text("---\n"+yaml.safe_dump(d,sort_keys=False,allow_unicode=True)+"---\n"+body.lstrip("\n"))
PY
check M3_board_no_waiver 1; restore

echo "--- M4: canonical with empty promotion_history ---"
python3 - <<'PY'
import yaml,pathlib
p=pathlib.Path("content/physics/measurement-units/metre.md"); raw=p.read_text(); fm,body=raw.split("---",2)[1],raw.split("---",2)[2]
d=yaml.safe_load(fm); d["provenance"]["promotion_history"]=[]
p.write_text("---\n"+yaml.safe_dump(d,sort_keys=False,allow_unicode=True)+"---\n"+body.lstrip("\n"))
PY
check M4_empty_history 1; restore

echo "--- M5: forward promotion while debt outstanding ---"
python3 - <<'PY'
import yaml,pathlib
p=pathlib.Path("content/physics/measurement-units/metre.md"); raw=p.read_text(); fm,body=raw.split("---",2)[1],raw.split("---",2)[2]
d=yaml.safe_load(fm)
# jump back to validator stage status while debt outstanding => forward move blocked
d["status"]="validator_validated"
d["provenance"]["promotion_history"]=[d["provenance"]["promotion_history"][0]]
p.write_text("---\n"+yaml.safe_dump(d,sort_keys=False,allow_unicode=True)+"---\n"+body.lstrip("\n"))
PY
check M5_debt_forward 1; restore

echo "--- M6: connection canonical with empty history ---"
python3 - <<'PY'
import yaml,pathlib
p=pathlib.Path("connections/conn.000156.yaml"); d=yaml.safe_load(p.read_text())
d["provenance"]["promotion_history"]=[]
p.write_text(yaml.safe_dump(d,sort_keys=False,allow_unicode=True))
PY
check M6_conn_no_history 1; restore

echo "--- M7: delete enforcement registry (fail closed) ---"
mv spec/machine-readable/enforcement_rules.yaml /tmp/enf.bak
check M7_no_registry 1
mv /tmp/enf.bak spec/machine-readable/enforcement_rules.yaml; restore

echo "--- restore + final baseline ---"; restore; check restored 0

if [ "$fail" -eq 0 ]; then echo "ALL MUTATIONS BEHAVED"; else echo "MUTATION SUITE FAILED"; fi
exit $fail
