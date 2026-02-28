from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import re
from typing import Any

import yaml
from yaml.nodes import MappingNode, ScalarNode, SequenceNode


ROOT = Path(__file__).resolve().parents[1]
AUTOMATIONS_PATH = ROOT / "config" / "automations.yaml"
CHECKLIST_PATH = ROOT / "appdaemon_config" / "automation_conversion_checklist.md"
OUT_PATH = ROOT / "appdaemon_config" / "automation_id_parity_matrix.md"


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


def parse_checklist_map(text: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    pattern = re.compile(r"^- \[[x~ ]\] `([^`]+)` -> (.+)$", re.MULTILINE)
    for m in pattern.finditer(text):
        alias = m.group(1).strip()
        target = m.group(2).strip()
        mapping[alias] = target
    return mapping


def summarize_triggers(item: dict[str, Any]) -> str:
    triggers = item.get("triggers") or item.get("trigger") or []
    if isinstance(triggers, dict):
        triggers = [triggers]

    parts: list[str] = []
    for tr in triggers:
        if not isinstance(tr, dict):
            continue
        t = str(tr.get("trigger", tr.get("platform", "unknown")))
        tid = tr.get("id")
        to_state = tr.get("to")
        duration = tr.get("for")

        detail: list[str] = [t]
        if tid:
            detail.append(f"id={tid}")
        if to_state is not None:
            detail.append(f"to={to_state}")
        if duration is not None:
            if isinstance(duration, dict):
                mins = duration.get("minutes")
                secs = duration.get("seconds")
                if mins is not None:
                    detail.append(f"for={mins}m")
                elif secs is not None:
                    detail.append(f"for={secs}s")
                else:
                    detail.append("for=<dict>")
            else:
                detail.append(f"for={duration}")
        parts.append(";".join(detail))

    return " / ".join(parts) if parts else "-"


def main() -> int:
    automations = load_yaml(AUTOMATIONS_PATH)
    checklist_text = CHECKLIST_PATH.read_text(encoding="utf-8")
    checklist_map = parse_checklist_map(checklist_text)

    entries: list[dict[str, Any]] = []
    for idx, item in enumerate(automations or [], start=1):
        if not isinstance(item, dict):
            continue
        alias = str(item.get("alias", "")).strip()
        if not alias:
            continue
        entries.append(
            {
                "index": idx,
                "id": str(item.get("id", "")).strip(),
                "alias": alias,
                "mode": str(item.get("mode", "single")).strip(),
                "trigger_summary": summarize_triggers(item),
            }
        )

    alias_counts = Counter(e["alias"] for e in entries)
    alias_occurrence: dict[str, int] = defaultdict(int)

    lines: list[str] = []
    lines.append("# Automation ID Parity Matrix")
    lines.append("")
    lines.append(f"- Source: `{AUTOMATIONS_PATH.relative_to(ROOT)}`")
    lines.append(f"- Checklist map: `{CHECKLIST_PATH.relative_to(ROOT)}`")
    lines.append(f"- Total entries with alias: **{len(entries)}**")
    lines.append(f"- Unique aliases: **{len(set(e['alias'] for e in entries))}**")
    lines.append("")
    lines.append("## Entry-Level Mapping")
    lines.append("")
    lines.append("| # | id | alias | occurrence | mode | trigger summary | mapped AppDaemon target | risk flags |")
    lines.append("|---|---|---|---|---|---|---|---|")

    unmapped = 0
    for e in entries:
        alias_occurrence[e["alias"]] += 1
        occ = alias_occurrence[e["alias"]]
        target = checklist_map.get(e["alias"], "UNMAPPED")
        if target == "UNMAPPED":
            unmapped += 1

        flags: list[str] = []
        if alias_counts[e["alias"]] > 1:
            flags.append("DUP_ALIAS")
        if e["mode"] in {"restart", "queued", "parallel"}:
            flags.append("MODE_SEMANTICS")
        if "for=" in e["trigger_summary"]:
            flags.append("FOR_DURATION")

        line = (
            f"| {e['index']} | `{e['id']}` | `{e['alias']}` | {occ}/{alias_counts[e['alias']]} | "
            f"`{e['mode']}` | {e['trigger_summary']} | {target} | {', '.join(flags) if flags else '-'} |"
        )
        lines.append(line)

    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Unmapped entries: **{unmapped}**")
    lines.append("- `DUP_ALIAS`: same alias appears multiple times in source, validate each entry-level behavior")
    lines.append("- `MODE_SEMANTICS`: requires explicit rapid retrigger test for HA mode parity")
    lines.append("- `FOR_DURATION`: requires hold/break/re-enter duration tests")

    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    print(f"ENTRIES={len(entries)} UNMAPPED={unmapped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
