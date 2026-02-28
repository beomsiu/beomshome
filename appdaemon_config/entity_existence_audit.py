from __future__ import annotations

from pathlib import Path
import json
import re
import urllib.request
from typing import Any

import yaml
from yaml.nodes import MappingNode, ScalarNode, SequenceNode


ROOT = Path(__file__).resolve().parent
APPS_YAML = ROOT / "apps" / "apps.yaml"
SPECIAL_WELCOME = ROOT / "apps" / "special_modes" / "welcome_mode.yaml"
ROOM2_YAML = ROOT / "apps" / "room2" / "room2_room_core.yaml"
OUT = ROOT / "entity_existence_audit_report.md"
AD_STATE_URL = "http://127.0.0.1:5050/api/appdaemon/state"

ENTITY_RE = re.compile(r"^[a-z0-9_]+\.[a-z0-9_]+$")
SERVICE_OBJECT_NAMES = {
    "turn_on",
    "turn_off",
    "toggle",
    "start",
    "cancel",
    "set_value",
    "select_option",
    "media_stop",
    "volume_set",
    "speak",
}


class Loader(yaml.SafeLoader):
    pass


def _generic(loader: yaml.Loader, node: yaml.Node) -> Any:
    if isinstance(node, ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, MappingNode):
        return loader.construct_mapping(node)
    return None


Loader.add_constructor("!secret", _generic)
Loader.add_constructor("!include", _generic)
Loader.add_constructor("!include_dir_merge_named", _generic)


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.load(fh, Loader=Loader)


def flatten_entities(node: Any, out: set[str]) -> None:
    if isinstance(node, dict):
        for v in node.values():
            flatten_entities(v, out)
        return
    if isinstance(node, list):
        for v in node:
            flatten_entities(v, out)
        return
    if isinstance(node, str) and ENTITY_RE.match(node):
        _domain, obj = node.split(".", 1)
        if obj not in SERVICE_OBJECT_NAMES:
            out.add(node)


def fetch_existing_entities() -> tuple[set[str], set[str]]:
    with urllib.request.urlopen(AD_STATE_URL, timeout=15) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    state = payload.get("state", {}) if isinstance(payload, dict) else {}
    default_ns = state.get("default", {}) if isinstance(state, dict) else {}
    admin_ns = state.get("admin", {}) if isinstance(state, dict) else {}
    return set(default_ns.keys()), set(admin_ns.keys())


def main() -> int:
    default_entities, admin_entities = fetch_existing_entities()
    known_domains = {e.split(".", 1)[0] for e in default_entities if "." in e}

    entities: set[str] = set()
    for p in (APPS_YAML, SPECIAL_WELCOME, ROOM2_YAML):
        if p.exists():
            flatten_entities(load_yaml(p), entities)

    filtered_entities = {
        e
        for e in entities
        if e.startswith("app.") or e.split(".", 1)[0] in known_domains
    }

    missing_default = sorted(e for e in filtered_entities if e not in default_entities and not e.startswith("app."))
    app_entities = sorted(e for e in filtered_entities if e.startswith("app."))
    missing_admin_apps = sorted(e for e in app_entities if e not in admin_entities)

    lines: list[str] = []
    lines.append("# Entity Existence Audit Report")
    lines.append("")
    lines.append("Live source: AppDaemon API `/api/appdaemon/state`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total referenced entities parsed: **{len(entities)}**")
    lines.append(f"- Entities after domain filtering: **{len(filtered_entities)}**")
    lines.append(f"- Missing in `default` namespace: **{len(missing_default)}**")
    lines.append(f"- Missing app entities in `admin` namespace: **{len(missing_admin_apps)}**")
    lines.append("")

    if missing_default:
        lines.append("## Missing Default Namespace Entities")
        lines.append("")
        for e in missing_default:
            lines.append(f"- `{e}`")
        lines.append("")

    if missing_admin_apps:
        lines.append("## Missing Admin App Entities")
        lines.append("")
        for e in missing_admin_apps:
            lines.append(f"- `{e}`")
        lines.append("")

    lines.append("## Notes")
    lines.append("")
    lines.append("- This is a non-invasive preflight check (no state changes/actions sent).")
    lines.append("- Existence does not guarantee behavior parity; runtime trigger tests are still required.")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    print(
        f"REFERENCED={len(entities)} FILTERED={len(filtered_entities)} "
        f"MISSING_DEFAULT={len(missing_default)} MISSING_ADMIN_APPS={len(missing_admin_apps)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
