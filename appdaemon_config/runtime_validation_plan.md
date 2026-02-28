# AppDaemon Runtime Validation Plan

This is a one-pass parity validation plan for converted automations from `config/automations.yaml`.
Mapping source: `appdaemon_config/automation_conversion_checklist.md`.

For copy-paste HA Developer Tools actions (hard cases), use `appdaemon_config/ha_service_calls.md`.

## 1) Start and Observe

Run from `homeassistant/`:

```bash
docker compose up -d appdaemon
docker logs -f appdaemon_config
```

You should see app initialization logs for room/mode cores and features.

## 2) Trigger-by-Trigger Validation

For each row, trigger from HA UI (entity toggle/state simulation) and confirm expected state + AppDaemon log lines.

| Alias (from automations.yaml) | Trigger to test | Expected result |
|---|---|---|
| room3 manual mode | Toggle `switch.room3_l1_l1` physically | `input_boolean.room3_manualmode_on` ON and `timer.room3_manualmode_timer` starts |
| room3 last light tracker | Turn `light.room3_l1_1` on/off | `input_select.room3_lastlight` reflects `l1/l2/both/none` |
| room3 sleep mode | Set `input_boolean.room3_sleepmode_on` ON/OFF | Sleep ON: room3 lights off + notify/TTS; OFF: wake notify/TTS |
| room3 button switch sleeping mode trigger & sublight control | Single/double/hold on knob action sensor | Single cycles color, double toggles nap, hold toggles sleep |
| bathroom1 light automation | Raise `number.bath1_c1_people` above `0.5` then below | Lights/fan/switch behavior follows occupancy and off branch |
| kitchen light automation | `binary_sensor.kitchen_m1_presence` ON then OFF | Kitchen lights on, then off per timeout/home mode branch |
| living light automation | `binary_sensor.living_m1_presence` ON then OFF | Living lights on in low lux, off after timeout branch |
| kitchen manual mode | Physical kitchen switch toggle | Manual boolean ON and timer behavior matches restart rules |
| living manual mode | Physical living switch toggle | Manual boolean/timer/find switch behavior matches YAML logic |
| front door alert | Keep door contact ON > 60s, then OFF | Alert notify/TTS/flash while open; close reset on OFF |
| room3 sleep mode off by time | Set wake time near now and wait | Sleep/manual booleans OFF + room3 lights wake-on + weather notify |
| bath1 fan automation | Humidity cross target above/below | `switch.bath1_f1` ON at high humidity, OFF after low duration |
| nap mode | Toggle `input_boolean.room3_napmode_on` ON then OFF | Nap start actions + timer, then wake restore actions |
| nap mode timer out | Let nap timer finish | Nap toggle auto OFF and end notifications/TTS fire |
| room3 light correction | Radar ON while people counter is 0 | `number.room3_c1_people` corrected to 1 |
| room3 light automation | Counter >0.5 then <=0.5 and no radar | Room3 light on/off branches execute with manual mode guard |
| away mode | Set all persons to `not_home`, then one to `home` | Away boolean ON after delay; OFF when someone returns |
| bath1 relax mode | Toggle `input_boolean.bath1_relaxmode_on` and change color select | Relax scene applies and updates color theme live |
| living movie mode | Toggle movie boolean and TV state transitions | Snapshot/dim/pause/resume/restore branches behave correctly |
| repair mode | Toggle `input_boolean.common_repairmode_on` | Features are guarded (paused) and resume on OFF |
| bath1 light settings default | Move bath1 sliders and turn bath1 lights on | Slider sync and on-apply behavior matches defaults |
| bar light settings default | Move bar sliders and turn bar lights on | `light.bar_lights` updated to slider brightness/kelvin |
| bathroom2 light automation | Bath2 people counter/status transitions | Bath2 light/fan/switch control matches occupancy branches |
| balcony1 light automation | Presence ON/OFF with sun below horizon | `switch.balcony1_l1` ON/OFF only when sun condition passes |
| cooking mode | Induction ON/OFF and cooking timer toggle | Cooking mode/timer/notify/light snapshot sequence works |
| bar light automation | Bar presence ON/OFF | Bar lights on and delayed off branch works |
| nap mode timer | Change `input_number.nap_duration_input` then start nap | Nap timer starts with updated duration |
| welcome mode | Door opens, then stays closed for 3 min with no living presence | Living welcome scene ON at open; OFF after delayed close |
| room2 light automation | `binary_sensor.room2_m1_presence` ON then OFF | `switch.room2_l2` ON/OFF immediately |

## 3) Pass/Fail Recording Template

Use this quick format while testing:

```text
[PASS] room3 manual mode - trigger: switch.room3_l1_l1 physical toggle - observed: manual boolean on, timer started
[PASS] welcome mode - trigger: door open/close duration - observed: living_l3 lights on then off after 180s
[FAIL] living movie mode - trigger: TV paused - observed: hall light did not restore
```

## 4) Exit Criteria

- All aliases from `automations.yaml` marked PASS at least once.
- No AppDaemon traceback/errors during full run.
- Any FAIL has exact reproduction trigger + timestamp captured from `docker logs -f appdaemon_config`.
