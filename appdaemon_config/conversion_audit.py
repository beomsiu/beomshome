from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
from typing import Any

import yaml
from yaml.nodes import MappingNode, ScalarNode, SequenceNode


ROOT = Path(__file__).resolve().parents[1]
AUTOMATIONS_PATH = ROOT / "config" / "automations.yaml"
CONFIGURATION_PATH = ROOT / "config" / "configuration.yaml"
CHECKLIST_PATH = ROOT / "appdaemon_config" / "automation_conversion_checklist.md"
APPS_PATH = ROOT / "appdaemon_config" / "apps" / "apps.yaml"
OUT_PATH = ROOT / "appdaemon_config" / "conversion_audit_report.md"


class SafeLoaderWithSecrets(yaml.SafeLoader):
    pass


def _secret_constructor(loader: yaml.Loader, node: yaml.Node) -> Any:
    if isinstance(node, ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, MappingNode):
        return loader.construct_mapping(node)
    return None


SafeLoaderWithSecrets.add_constructor("!secret", _secret_constructor)
SafeLoaderWithSecrets.add_constructor("!include", _secret_constructor)
SafeLoaderWithSecrets.add_constructor("!include_dir_merge_named", _secret_constructor)


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.load(fh, Loader=SafeLoaderWithSecrets)


def collect_aliases(automations: list[dict[str, Any]]) -> list[str]:
    aliases: list[str] = []
    for item in automations:
        alias = item.get("alias")
        if alias:
            aliases.append(str(alias).strip())
    return aliases


def parse_checklist_aliases(text: str) -> list[str]:
    aliases: list[str] = []
    pattern = re.compile(r"^- \[[x~ ]\] `([^`]+)`", re.MULTILINE)
    for m in pattern.finditer(text):
        aliases.append(m.group(1).strip())
    return aliases


def collect_entity_domains(value: Any) -> Counter:
    domains: Counter = Counter()

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if k in {"entity_id", "entity_ids"}:
                    for ent in normalize_entities(v):
                        if "." in ent:
                            domains[ent.split(".", 1)[0]] += 1
                walk(v)
        elif isinstance(node, list):
            for x in node:
                walk(x)

    walk(value)
    return domains


def normalize_entities(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple, set)):
        return [str(v) for v in value]
    return [str(value)]


def main() -> int:
    automations = load_yaml(AUTOMATIONS_PATH)
    configuration = load_yaml(CONFIGURATION_PATH)
    apps = load_yaml(APPS_PATH)
    checklist_text = CHECKLIST_PATH.read_text(encoding="utf-8")

    aliases = collect_aliases(automations)
    checklist_aliases = parse_checklist_aliases(checklist_text)

    alias_set = set(aliases)
    checklist_set = set(checklist_aliases)
    alias_counts = Counter(aliases)
    duplicate_aliases = sorted([name for name, count in alias_counts.items() if count > 1])

    missing_in_checklist = sorted(alias_set - checklist_set)
    stale_in_checklist = sorted(checklist_set - alias_set)

    app_keys = sorted(apps.keys()) if isinstance(apps, dict) else []
    domains = collect_entity_domains(automations)

    lines: list[str] = []
    lines.append("# Conversion Audit Report")
    lines.append("")
    lines.append(f"- Source automations: `{AUTOMATIONS_PATH.relative_to(ROOT)}`")
    lines.append(f"- Source configuration: `{CONFIGURATION_PATH.relative_to(ROOT)}`")
    lines.append(f"- Checklist: `{CHECKLIST_PATH.relative_to(ROOT)}`")
    lines.append(f"- App registry: `{APPS_PATH.relative_to(ROOT)}`")
    lines.append("")
    lines.append("## Alias Coverage")
    lines.append("")
    lines.append(f"- Automations entries with alias: **{len(aliases)}**")
    lines.append(f"- Unique automations aliases: **{len(alias_set)}**")
    lines.append(f"- Checklist aliases found: **{len(checklist_aliases)}**")
    lines.append(f"- Unique checklist aliases: **{len(checklist_set)}**")
    lines.append(f"- Missing in checklist: **{len(missing_in_checklist)}**")
    lines.append(f"- Extra in checklist: **{len(stale_in_checklist)}**")
    lines.append("")

    if duplicate_aliases:
        lines.append("### Duplicate Alias Names in automations.yaml")
        lines.append("")
        for name in duplicate_aliases:
            lines.append(f"- {name} ({alias_counts[name]} entries)")
        lines.append("")

    if missing_in_checklist:
        lines.append("### Missing in Checklist")
        lines.append("")
        lines.extend(f"- {alias}" for alias in missing_in_checklist)
        lines.append("")

    if stale_in_checklist:
        lines.append("### Present in Checklist but not in automations.yaml")
        lines.append("")
        lines.extend(f"- {alias}" for alias in stale_in_checklist)
        lines.append("")

    lines.append("## Dependency Inventory (from automations entity references)")
    lines.append("")
    for domain, count in domains.most_common():
        lines.append(f"- `{domain}`: {count}")
    lines.append("")

    lines.append("## Helper Domains in configuration.yaml")
    lines.append("")
    for domain in ["input_boolean", "input_number", "input_select", "timer", "template", "scene", "script"]:
        status = "present" if domain in configuration else "absent"
        lines.append(f"- `{domain}`: {status}")
    lines.append("")

    lines.append("## AppDaemon Apps Registered")
    lines.append("")
    lines.append(f"- Total app entries in apps.yaml: **{len(app_keys)}**")
    lines.append("")
    for app in app_keys:
        lines.append(f"- `{app}`")

    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_PATH}")
    print(f"ALIASES={len(aliases)} CHECKLIST={len(checklist_aliases)} MISSING={len(missing_in_checklist)} EXTRA={len(stale_in_checklist)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
