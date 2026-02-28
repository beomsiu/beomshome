# Home Assistant -> AppDaemon Conversion Checklist

Source reviewed:
- `config/automations.yaml`
- `config/configuration.yaml`

Status legend:
- `[x]` transformed to AppDaemon
- `[~]` transformed by merged/shared AppDaemon feature (no separate 1:1 app needed)

- [x] `room3 manual mode` -> `apps.yaml` `room3_room_core.features.manual_mode`
- [x] `room3 last light tracker` -> `apps.yaml` `room3_room_core.features.last_light_tracker`
- [x] `room3 sleep mode` -> `apps.yaml` `room3_sleep_mode` + `room3_room_core.features.sleep_light`
- [x] `room3 button switch sleeping mode trigger & sublight control` -> `apps.yaml` `room3_room_core.features.knob_control`
- [x] `bathroom1 light automation` -> `apps.yaml` `bathroom1_room_core.features.people_lighting`
- [x] `kitchen light automation` -> `apps.yaml` `kitchen_room_core.features.presence_lighting`
- [x] `living light automation` -> `apps.yaml` `living_room_core.features.presence_lighting`
- [x] `kitchen manual mode` -> `apps.yaml` `kitchen_room_core.features.manual_mode`
- [x] `living manual mode` -> `apps.yaml` `living_room_core.features.manual_mode`
- [x] `front door alert` -> `apps.yaml` `entry_alarm.features.door_alert`
- [x] `room3 sleep mode off by time` -> `apps.yaml` `room3_room_core.features.sleepmode_off`
- [x] `bath1 fan automation` -> `apps.yaml` `bathroom1_room_core.features.humidity_fan`
- [x] `nap mode` -> `apps.yaml` `nap_mode.features.nap_control`
- [~] `nap mode timer out` -> merged into `mode_nap` timer-finished handling (`nap_mode.features.nap_control`)
- [x] `room3 light correction` -> `apps.yaml` `room3_room_core.features.light_correction`
- [x] `room3 light automation` -> `apps.yaml` `room3_room_core.features.counter_presence`
- [x] `away mode` -> `apps.yaml` `away_mode.features.family_presence`
- [x] `bath1 relax mode` -> `apps.yaml` `bath1_relax_mode.features.relax_scene`
- [x] `living movie mode` -> `apps.yaml` `living_movie_mode.features.movie_scene`
- [x] `repair mode` -> `apps.yaml` `repair_mode.features.automation_pause`
- [x] `bath1 light settings default` -> `apps.yaml` `bathroom1_room_core.features.light_settings`
- [x] `bar light settings default` -> `apps.yaml` `bar_room_core.features.light_settings_sync`
- [x] `bathroom2 light automation` -> `apps.yaml` `bathroom2_room_core.features.people_lighting`
- [x] `balcony1 light automation` -> `apps.yaml` `balcony1_room_core.features.balcony_presence`
- [x] `cooking mode` -> `apps.yaml` `cooking_mode.features.induction_monitor`
- [x] `bar light automation` -> `apps.yaml` `bar_room_core.features.presence_lighting`
- [~] `nap mode timer` -> merged into `mode_nap` duration input + timer start logic (`nap_mode.features.nap_control.duration_entity`)
- [x] `welcome mode` -> `apps.yaml` `welcome_mode.features.door_open_scene`, `welcome_mode.features.door_closed_scene_clear`
- [x] `room2 light automation` -> `apps.yaml` `room2_room_core.features.presence_lighting`

## Notes

- `configuration.yaml` includes `automations.yaml` and helper domains; helper parity is handled by `global_helper_manager` in `appdaemon_config/apps/apps.yaml`.
- `welcome mode` and `room2 light automation` were newly added in this conversion pass.
- `nap mode timer` + `nap mode timer out` are intentionally consolidated into `mode_nap` to preserve behavior while removing duplicated YAML automation paths.
