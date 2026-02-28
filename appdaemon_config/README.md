# AppDaemon Project Layout

This repository stores AppDaemon-first automation assets migrated from Home Assistant YAML automations.

## Key Files

- `apps/apps.yaml`: main app registry
- `apps/base/`: reusable feature code
- `automation_conversion_checklist.md`: alias-level conversion map
- `automation_id_parity_matrix.md`: id-level (entry-level) parity map
- `runtime_validation_plan.md`: runtime verification steps
- `ha_service_calls.md`: copy-paste HA Developer Tools actions
- `master_conversion_runbook.md`: end-to-end execution and cutover checklist

## Additional Audits

- `conversion_audit.py` + `conversion_audit_report.md`
- `entity_existence_audit.py` + `entity_existence_audit_report.md`
- `generate_id_parity_matrix.py` + `automation_id_parity_matrix.md`
