# Automation ID Parity Matrix

- Source: `config/automations.yaml`
- Checklist map: `appdaemon_config/automation_conversion_checklist.md`
- Total entries with alias: **40**
- Unique aliases: **29**

## Entry-Level Mapping

| # | id | alias | occurrence | mode | trigger summary | mapped AppDaemon target | risk flags |
|---|---|---|---|---|---|---|---|
| 1 | `302` | `room3 manual mode` | 1/1 | `restart` | state;id=physical_switch / event;id=timer_end / state;id=radar_off;to=off;for=5m / state;id=manual_mode_off;to=off | `apps.yaml` `room3_room_core.features.manual_mode` | MODE_SEMANTICS, FOR_DURATION |
| 2 | `304` | `room3 last light tracker` | 1/1 | `restart` | state | `apps.yaml` `room3_room_core.features.last_light_tracker` | MODE_SEMANTICS |
| 3 | `305` | `room3 sleep mode` | 1/1 | `single` | state;id=sleep_on;to=on / state;id=sleep_off;to=off | `apps.yaml` `room3_sleep_mode` + `room3_room_core.features.sleep_light` | - |
| 4 | `307` | `room3 button switch sleeping mode trigger & sublight control` | 1/1 | `single` | - | `apps.yaml` `room3_room_core.features.knob_control` | - |
| 5 | `1100` | `bathroom1 light automation` | 1/1 | `restart` | numeric_state;id=present / state;id=present;to=in / numeric_state;id=absence_event / state;id=force_off;to=off;for=00:00:05 / time_pattern;id=safety_check | `apps.yaml` `bathroom1_room_core.features.people_lighting` | MODE_SEMANTICS, FOR_DURATION |
| 6 | `1761078104645` | `kitchen light automation` | 1/1 | `restart` | state;id=present_1;to=on / state;id=absence_correction;to=off / time_pattern;id=safety_check | `apps.yaml` `kitchen_room_core.features.presence_lighting` | MODE_SEMANTICS |
| 7 | `1761080716782` | `living light automation` | 1/1 | `restart` | state;id=present;to=on / state;id=absence;to=off;for=1m / time_pattern;id=safety_check | `apps.yaml` `living_room_core.features.presence_lighting` | MODE_SEMANTICS, FOR_DURATION |
| 8 | `1761606258063` | `kitchen manual mode` | 1/1 | `restart` | state;id=physical_switch / event;id=timer_end / state;id=manual_off;to=off | `apps.yaml` `kitchen_room_core.features.manual_mode` | MODE_SEMANTICS |
| 9 | `1761866430270` | `living manual mode` | 1/1 | `restart` | state;id=living_manual_on / event;id=living_manual_timeout / state;id=mode_change | `apps.yaml` `living_room_core.features.manual_mode` | MODE_SEMANTICS |
| 10 | `front_door_alert_combined` | `front door alert` | 1/1 | `restart` | state;id=door_open;to=on / state;id=door_still_open;to=on;for=1m / state;id=door_closed;to=off | `apps.yaml` `entry_alarm.features.door_alert` | MODE_SEMANTICS, FOR_DURATION |
| 11 | `1762940863350` | `room3 sleep mode off by time` | 1/1 | `single` | time | `apps.yaml` `room3_room_core.features.sleepmode_off` | - |
| 12 | `1765228312862` | `bath1 fan automation` | 1/1 | `restart` | numeric_state;id=humidity_high / numeric_state;id=humidity_low;for=1m | `apps.yaml` `bathroom1_room_core.features.humidity_fan` | MODE_SEMANTICS, FOR_DURATION |
| 13 | `nap_mode_automation` | `nap mode` | 1/3 | `restart` | state;id=nap on;to=on / state;id=nap off;to=off | `apps.yaml` `nap_mode.features.nap_control` | DUP_ALIAS, MODE_SEMANTICS |
| 14 | `1765430730366` | `nap mode timer out` | 1/1 | `single` | event | merged into `mode_nap` timer-finished handling (`nap_mode.features.nap_control`) | - |
| 15 | `1765440811452` | `room3 light correction` | 1/1 | `restart` | numeric_state;id=counter_is_zero / state;id=radar_is_on;to=on | `apps.yaml` `room3_room_core.features.light_correction` | MODE_SEMANTICS |
| 16 | `1765440900076` | `room3 light automation` | 1/1 | `restart` | numeric_state;id=present / numeric_state;id=absence_event;for=00:01:00 / state;id=force_off;to=off;for=00:01:00 / state;id=force_off;to=off;for=00:01:00 / time_pattern;id=safety_check | `apps.yaml` `room3_room_core.features.counter_presence` | MODE_SEMANTICS, FOR_DURATION |
| 17 | `1765881344963` | `away mode` | 1/1 | `restart` | state;id=location_change | `apps.yaml` `away_mode.features.family_presence` | MODE_SEMANTICS |
| 18 | `1765884427826` | `bath1 relax mode` | 1/1 | `single` | state;id=start_relax_mode;to=on / state;id=end_relax_mode;to=off / state;id=color_change | `apps.yaml` `bath1_relax_mode.features.relax_scene` | - |
| 19 | `1766018245659` | `living movie mode` | 1/1 | `restart` | state;id=movie_start;to=on / state;id=movie_stop;to=off / state;id=movie_start_tv;to=playing;for=3s / state;id=movie_resume;to=playing;for=2s / state;id=movie_paused;to=paused;for=1s / state;id=movie_stop_tv;to=['off', 'idle', 'standby', 'unavailable', 'unknown'] | `apps.yaml` `living_movie_mode.features.movie_scene` | MODE_SEMANTICS, FOR_DURATION |
| 20 | `1766041345921` | `repair mode` | 1/1 | `restart` | state | `apps.yaml` `repair_mode.features.automation_pause` | MODE_SEMANTICS |
| 21 | `1766749220232` | `bath1 light settings default` | 1/1 | `restart` | state;id=slider_moved / state;id=light_turned_on;to=on | `apps.yaml` `bathroom1_room_core.features.light_settings` | MODE_SEMANTICS |
| 22 | `1766750701342` | `bar light settings default` | 1/1 | `restart` | state;id=slider_moved / state;id=light_turned_on;to=on | `apps.yaml` `bar_room_core.features.light_settings_sync` | MODE_SEMANTICS |
| 23 | `1768989076337` | `bathroom2 light automation` | 1/1 | `restart` | numeric_state;id=present / state;id=present_1;to=in / numeric_state;id=absent | `apps.yaml` `bathroom2_room_core.features.people_lighting` | MODE_SEMANTICS |
| 24 | `1769607888891` | `balcony1 light automation` | 1/1 | `single` | state;id=presence;to=on / state;id=absence;to=off | `apps.yaml` `balcony1_room_core.features.balcony_presence` | - |
| 25 | `cooking_mode_automation` | `cooking mode` | 1/10 | `restart` | state;id=induction_on;to=on / state;id=induction_off;to=off / state;id=timer_toggle_on;to=on / state;id=timer_toggle_off;to=off / event;id=timer_finished | `apps.yaml` `cooking_mode.features.induction_monitor` | DUP_ALIAS, MODE_SEMANTICS |
| 26 | `cooking_mode_automation` | `cooking mode` | 2/10 | `restart` | state;id=induction_on;to=on / state;id=induction_off;to=off / state;id=timer_toggle_on;to=on / state;id=timer_toggle_off;to=off / event;id=timer_finished | `apps.yaml` `cooking_mode.features.induction_monitor` | DUP_ALIAS, MODE_SEMANTICS |
| 27 | `cooking_mode_automation` | `cooking mode` | 3/10 | `restart` | state;id=induction_on;to=on / state;id=induction_off;to=off / state;id=timer_toggle_on;to=on / state;id=timer_toggle_off;to=off / event;id=timer_finished | `apps.yaml` `cooking_mode.features.induction_monitor` | DUP_ALIAS, MODE_SEMANTICS |
| 28 | `cooking_mode_automation` | `cooking mode` | 4/10 | `restart` | state;id=induction_on;to=on / state;id=induction_off;to=off / state;id=timer_toggle_on;to=on / state;id=timer_toggle_off;to=off / event;id=timer_finished | `apps.yaml` `cooking_mode.features.induction_monitor` | DUP_ALIAS, MODE_SEMANTICS |
| 29 | `cooking_mode_automation` | `cooking mode` | 5/10 | `restart` | state;id=induction_on;to=on / state;id=induction_off;to=off / state;id=timer_toggle_on;to=on / state;id=timer_toggle_off;to=off / event;id=timer_finished | `apps.yaml` `cooking_mode.features.induction_monitor` | DUP_ALIAS, MODE_SEMANTICS |
| 30 | `cooking_mode_automation` | `cooking mode` | 6/10 | `restart` | state;id=induction_on;to=on / state;id=induction_off;to=off / state;id=timer_toggle_on;to=on / state;id=timer_toggle_off;to=off / event;id=timer_finished | `apps.yaml` `cooking_mode.features.induction_monitor` | DUP_ALIAS, MODE_SEMANTICS |
| 31 | `cooking_mode_automation` | `cooking mode` | 7/10 | `restart` | state;id=induction_on;to=on / state;id=induction_off;to=off / state;id=timer_toggle_on;to=on / state;id=timer_toggle_off;to=off / event;id=timer_finished | `apps.yaml` `cooking_mode.features.induction_monitor` | DUP_ALIAS, MODE_SEMANTICS |
| 32 | `cooking_mode_automation` | `cooking mode` | 8/10 | `restart` | state;id=induction_on;to=on / state;id=induction_off;to=off / state;id=timer_toggle_on;to=on / state;id=timer_toggle_off;to=off / event;id=timer_finished | `apps.yaml` `cooking_mode.features.induction_monitor` | DUP_ALIAS, MODE_SEMANTICS |
| 33 | `cooking_mode_automation` | `cooking mode` | 9/10 | `restart` | state;id=induction_on;to=on / state;id=induction_off;to=off / state;id=timer_toggle_on;to=on / state;id=timer_toggle_off;to=off / event;id=timer_finished | `apps.yaml` `cooking_mode.features.induction_monitor` | DUP_ALIAS, MODE_SEMANTICS |
| 34 | `cooking_mode_automation` | `cooking mode` | 10/10 | `restart` | state;id=induction_on;to=on / state;id=induction_off;to=off / state;id=timer_toggle_on;to=on / state;id=timer_toggle_off;to=off / event;id=timer_finished | `apps.yaml` `cooking_mode.features.induction_monitor` | DUP_ALIAS, MODE_SEMANTICS |
| 35 | `nap_mode_automation` | `nap mode` | 2/3 | `restart` | state;id=nap on;to=on / state;id=nap off;to=off | `apps.yaml` `nap_mode.features.nap_control` | DUP_ALIAS, MODE_SEMANTICS |
| 36 | `nap_mode_automation` | `nap mode` | 3/3 | `restart` | state;id=nap on;to=on / state;id=nap off;to=off | `apps.yaml` `nap_mode.features.nap_control` | DUP_ALIAS, MODE_SEMANTICS |
| 37 | `1770392800899` | `bar light automation` | 1/1 | `restart` | state;id=present;to=on / state;id=absence_correction;to=off / time_pattern;id=safety_check | `apps.yaml` `bar_room_core.features.presence_lighting` | MODE_SEMANTICS |
| 38 | `1770517219483` | `nap mode timer` | 1/1 | `restart` | state | merged into `mode_nap` duration input + timer start logic (`nap_mode.features.nap_control.duration_entity`) | MODE_SEMANTICS |
| 39 | `1770521189343` | `welcome mode` | 1/1 | `restart` | state;id=door_open;to=on / state;id=door_closed_long;to=off;for=3m | `apps.yaml` `welcome_mode.features.door_open_scene`, `welcome_mode.features.door_closed_scene_clear` | MODE_SEMANTICS, FOR_DURATION |
| 40 | `1770525254835` | `room2 light automation` | 1/1 | `single` | state;id=present;to=on / state;id=absent;to=off | `apps.yaml` `room2_room_core.features.presence_lighting` | - |

## Summary

- Unmapped entries: **0**
- `DUP_ALIAS`: same alias appears multiple times in source, validate each entry-level behavior
- `MODE_SEMANTICS`: requires explicit rapid retrigger test for HA mode parity
- `FOR_DURATION`: requires hold/break/re-enter duration tests
