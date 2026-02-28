# Master Conversion Runbook (HA -> AppDaemon)

This is the single execution sheet to reach exact conversion parity from:
- `config/automations.yaml`
- `config/configuration.yaml`

## A) Completed by Agent (already executed)

- [x] Added missing AppDaemon implementations:
  - `welcome_mode` in `appdaemon_config/apps/apps.yaml`
  - `room2_room_core` in `appdaemon_config/apps/apps.yaml`
- [x] Extended trigger parity support in `appdaemon_config/apps/base/mode_features/mode_presence_trigger.py` for declarative trigger objects with `to`, `from`, `duration` (`for:` equivalent).
- [x] Built alias checklist in `appdaemon_config/automation_conversion_checklist.md`.
- [x] Added runtime validation matrix in `appdaemon_config/runtime_validation_plan.md`.
- [x] Added copy-paste HA test actions in `appdaemon_config/ha_service_calls.md`.
- [x] Added automated audit script/report:
  - Script: `appdaemon_config/conversion_audit.py`
  - Report: `appdaemon_config/conversion_audit_report.md`
- [x] Added id-level parity matrix generation (Oracle recommendation):
  - Script: `appdaemon_config/generate_id_parity_matrix.py`
  - Report: `appdaemon_config/automation_id_parity_matrix.md`
- [x] Verified AppDaemon runtime loads new apps via admin API (`app.welcome_mode`, `app.room2_room_core` present and idle).

## B) Audit Snapshot (current)

- [x] Alias coverage parity: 29 unique aliases in source and 29 unique aliases in checklist.
- [x] Entry coverage parity: 40/40 automation entries mapped (id-level matrix).
- [x] Missing aliases in checklist: 0.
- [x] Extra aliases in checklist: 0.
- [x] AppDaemon apps registered: 21 (includes `welcome_mode`, `room2_room_core`).
- [x] Helper domains required by configuration are present (`input_boolean`, `input_number`, `input_select`, `timer`, `template`, `scene`, `script`).

## C) Commands to Re-run Evidence

From `homeassistant/`:

```bash
python3 appdaemon_config/conversion_audit.py
python3 appdaemon_config/generate_id_parity_matrix.py
docker compose up -d appdaemon
curl -sS "http://127.0.0.1:5050/api/appdaemon/state" > /tmp/ad_state.json
python3 - <<'PY'
import json
from pathlib import Path
obj=json.loads(Path('/tmp/ad_state.json').read_text(encoding='utf-8'))
admin=obj.get('state',{}).get('admin',{})
for key in sorted(['app.welcome_mode','app.room2_room_core','sensor.active_apps','sensor.inactive_apps']):
    val=admin.get(key,{})
    print(key, val.get('state'))
PY
```

Expected:
- `app.welcome_mode idle`
- `app.room2_room_core idle`
- `sensor.inactive_apps 0`

## D) Manual Runtime Parity Test (required for final acceptance)

Execute all alias tests in:
- `appdaemon_config/runtime_validation_plan.md`

Use ready-to-paste actions in:
- `appdaemon_config/ha_service_calls.md`

Mark PASS/FAIL for each alias with timestamp and observed state/log output.

Additionally run Oracle-priority probes from `appdaemon_config/automation_id_parity_matrix.md`:
- all rows tagged `MODE_SEMANTICS` (rapid retrigger behavior)
- all rows tagged `FOR_DURATION` (hold/break/re-enter behavior)
- all rows tagged `DUP_ALIAS` (validate each duplicate entry behavior explicitly)

## E) Cutover Gate (must all be true)

- [ ] Every alias test has at least one PASS.
- [ ] Every id-level matrix row (40 rows) has at least one PASS.
- [ ] No AppDaemon traceback during full test pass.
- [ ] Any failures were fixed and re-tested to PASS.
- [ ] Only after all PASS: disable overlapping HA automations.

## F) Rollback Plan

If a critical regression appears:
1. Re-enable corresponding HA automation(s).
2. Keep AppDaemon app running for targeted logs.
3. Patch AppDaemon feature, then re-run only failed alias tests and the final full pass.
