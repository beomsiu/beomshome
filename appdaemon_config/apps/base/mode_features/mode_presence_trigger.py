from __future__ import annotations
from typing import Any, Dict, List

from .action_utils import run_actions
from .mode_feature import ModeFeature


class ModePresenceTriggerFeature(ModeFeature):
    """Run declarative actions when a presence entity enters specific states."""

    feature_name = "mode_presence_trigger"

    def initialize(self):
        self.presence_entity = self.require("presence_entity")
        self.trigger_states: List[str] = list(self.config.get("trigger_states", []) or [])
        self.triggers: List[Dict[str, Any]] = list(self.config.get("triggers", []) or [])
        self.target_states: List[str] = list(self.config.get("target_states", []) or [])
        self.conditions: List[Dict[str, Any]] = list(self.config.get("conditions", []) or [])
        self.actions: List[Dict[str, Any]] = list(self.config.get("actions", []) or [])
        self.log_transitions = bool(self.config.get("log_transitions", True))

        if self.triggers:
            for trigger in self.triggers:
                if not isinstance(trigger, dict):
                    continue
                kwargs: Dict[str, Any] = {}
                new_state = trigger.get("to")
                if new_state is None:
                    new_state = trigger.get("new")
                old_state = trigger.get("from")
                duration = trigger.get("duration")

                if new_state is not None:
                    kwargs["new"] = str(new_state)
                if old_state is not None:
                    kwargs["old"] = str(old_state)
                if duration is not None:
                    kwargs["duration"] = int(duration)

                self.listen_state(self._presence_changed, self.presence_entity, **kwargs)
        elif self.trigger_states:
            for state in self.trigger_states:
                self.listen_state(self._presence_changed, self.presence_entity, new=state)
        else:
            self.listen_state(self._presence_changed, self.presence_entity)

    # ------------------------------------------------------------------
    def _presence_changed(self, entity, attribute, old, new, kwargs):
        if self.target_states and new not in self.target_states:
            return
        if not self._conditions_met():
            return

        if self.log_transitions:
            self.log(f"Presence changed {old} -> {new}")

        run_actions(self, self.actions)

    def _conditions_met(self) -> bool:
        for condition in self.conditions:
            if not self._check_condition(condition):
                return False
        return True

    def _check_condition(self, condition: Dict[str, Any]) -> bool:
        condition_type = condition.get("type", "state")

        if condition_type == "state":
            entity_id = condition.get("entity_id")
            expected_state = condition.get("state")
            if not entity_id:
                return False
            current_state = self.get_state(entity_id)
            return current_state == expected_state

        if condition_type == "not_state":
            entity_id = condition.get("entity_id")
            blocked_state = condition.get("state")
            if not entity_id:
                return True
            current_state = self.get_state(entity_id)
            return current_state != blocked_state

        return True
