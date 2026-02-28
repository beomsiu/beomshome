# Home Assistant Service Calls for AppDaemon Parity Tests

Use this with:
- HA UI -> Developer Tools -> Actions (service calls)
- HA UI -> Developer Tools -> States (for sensors/person/media state simulation)
- `docker logs -f appdaemon_config`

## 1) Nap Mode + Nap Timer (fast validation)

Set nap duration to 1 minute:

```yaml
service: input_number.set_value
target:
  entity_id: input_number.nap_duration_input
data:
  value: 1
```

Start nap mode:

```yaml
service: input_boolean.turn_on
target:
  entity_id: input_boolean.room3_napmode_on
```

Expected:
- `timer.room3_napmode_timer` starts around `00:01:00`
- room3 nap actions run
- when timer finishes, nap mode toggles OFF and end notifications/TTS run

Stop nap mode manually:

```yaml
service: input_boolean.turn_off
target:
  entity_id: input_boolean.room3_napmode_on
```

## 2) Living Movie Mode

Start movie mode:

```yaml
service: input_boolean.turn_on
target:
  entity_id: input_boolean.living_moviemode_on
```

Stop movie mode:

```yaml
service: input_boolean.turn_off
target:
  entity_id: input_boolean.living_moviemode_on
```

Optional TV state simulation (Developer Tools -> States):
- `media_player.geosil_tv1 = playing`
- `media_player.geosil_tv1 = paused`
- `media_player.geosil_tv1 = idle`

Expected:
- start branch: snapshot + dim/off targets + hall light path
- pause/resume branches react to TV state
- stop branch restores scene/fallback and clears manual/movie flags

## 3) Front Door Alert + Welcome Mode

Simulate door open/close in Developer Tools -> States:
- `binary_sensor.entrance_d1_contact = on` (open)
- keep `on` > 60s for door alert branch
- change to `off` for close branch

For welcome mode close-clear branch:
- keep `binary_sensor.entrance_d1_contact = off` for 180s
- keep `binary_sensor.living_m1_presence = off`

Expected:
- door alert: notify/TTS/light warning while open, reset on close
- welcome mode: living welcome scene ON on open, OFF after delayed close condition

## 4) Away Mode

Simulate person states in Developer Tools -> States:
- `person.beom = not_home`
- `person.family1 = not_home`
- `person.family2 = not_home`

Wait for confirm delay (~300s), then verify:
- `input_boolean.enterance_awaymode = on`

Return-home test:
- set any one person to `home`
- expect away mode OFF

## 5) Cooking Mode

Set timer minutes:

```yaml
service: input_number.set_value
target:
  entity_id: input_number.cooking_timer_minutes
data:
  value: 0.5
```

Enable cooking mode manually:

```yaml
service: input_boolean.turn_on
target:
  entity_id: input_boolean.cooking_mode
```

Start timer toggle:

```yaml
service: input_boolean.turn_on
target:
  entity_id: input_boolean.cooking_timer_toggle
```

Expected:
- `timer.cooking_mode_timer` starts
- completion notification/TTS and bar light snapshot/restore behavior

## 6) Quick Log Filter Commands

```bash
docker logs -f appdaemon_config
```

```bash
docker logs --since 5m appdaemon_config
```
