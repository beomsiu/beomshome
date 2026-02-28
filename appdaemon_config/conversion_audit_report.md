# Conversion Audit Report

- Source automations: `config/automations.yaml`
- Source configuration: `config/configuration.yaml`
- Checklist: `appdaemon_config/automation_conversion_checklist.md`
- App registry: `appdaemon_config/apps/apps.yaml`

## Alias Coverage

- Automations entries with alias: **40**
- Unique automations aliases: **29**
- Checklist aliases found: **29**
- Unique checklist aliases: **29**
- Missing in checklist: **0**
- Extra in checklist: **0**

### Duplicate Alias Names in automations.yaml

- cooking mode (10 entries)
- nap mode (3 entries)

## Dependency Inventory (from automations entity references)

- `light`: 150
- `input_boolean`: 116
- `binary_sensor`: 60
- `timer`: 58
- `automation`: 52
- `switch`: 35
- `tts`: 17
- `media_player`: 14
- `number`: 11
- `scene`: 11
- `sensor`: 8
- `input_number`: 6
- `input_select`: 4
- `person`: 3
- `sun`: 1

## Helper Domains in configuration.yaml

- `input_boolean`: present
- `input_number`: present
- `input_select`: present
- `timer`: present
- `template`: present
- `scene`: present
- `script`: present

## AppDaemon Apps Registered

- Total app entries in apps.yaml: **21**

- `away_mode`
- `balcony1_room_core`
- `bar_room_core`
- `bath1_relax_mode`
- `bathroom1_room_core`
- `bathroom2_room_core`
- `cooking_mode`
- `device_scanner`
- `entry_alarm`
- `global_helper_manager`
- `hello_world`
- `kitchen_room_core`
- `living_movie_mode`
- `living_room_core`
- `nap_mode`
- `repair_mode`
- `room2_room_core`
- `room3_room_core`
- `room3_sleep_mode`
- `update_manager`
- `welcome_mode`
