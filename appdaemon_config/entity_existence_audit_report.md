# Entity Existence Audit Report

Live source: AppDaemon API `/api/appdaemon/state`

## Summary

- Total referenced entities parsed: **99**
- Entities after domain filtering: **94**
- Missing in `default` namespace: **10**
- Missing app entities in `admin` namespace: **0**

## Missing Default Namespace Entities

- `light.bath1_l1_3`
- `person.beom`
- `person.family1`
- `person.family2`
- `sensor.bathroom2_humidity`
- `sensor.room3_switch_knob_action`
- `switch.living_switch_main_l1`
- `switch.living_switch_main_l2`
- `switch.living_switch_main_l3`
- `switch.living_switch_main_l4`

## Notes

- This is a non-invasive preflight check (no state changes/actions sent).
- Existence does not guarantee behavior parity; runtime trigger tests are still required.
