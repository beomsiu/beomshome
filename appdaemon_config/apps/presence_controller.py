from typing import Any, Dict, List, Optional

from base import SmartHomeBase


class PresenceLightController(SmartHomeBase):
    def initialize(self) -> None:
        super().initialize()

        self.presence_sensors: List[str] = self.args.get("presence_sensors", [])
        self.target_entities: List[str] = self.args.get("target_entities", [])
        self.turn_on_kwargs: Dict[str, Any] = self.args.get("turn_on_kwargs", {})
        self.turn_off_kwargs: Dict[str, Any] = self.args.get("turn_off_kwargs", {})

        self.manual_mode: Optional[str] = self.args.get("manual_mode")
        self.sun_dependent: bool = self.args.get("sun_dependent", False)

        self.base_turn_off_delay: int = self.args.get("base_turn_off_delay", 0)
        self.home_mode_entity: Optional[str] = self.args.get("home_mode_entity")
        self.comfort_mode_delay: int = self.args.get("comfort_mode_delay", 300)

        self.off_timer: Optional[str] = None

        for sensor in self.presence_sensors:
            self.listen_state(self.presence_handler, sensor)

        self.listen_event(self.live_sync_handler, "GLOBAL_LIGHT_SYNC")

    def presence_handler(
        self,
        entity: str,
        attribute: str,
        old: str,
        new: str,
        kwargs: Dict[str, Any],
    ) -> None:
        if new is None or new in self._UNAVAILABLE_STATES:
            return

        if self.manual_mode and self.get_state(self.manual_mode) == "on":
            self.log("Manual mode is active. Execution bypassed.", level="DEBUG")
            return

        is_anyone_present, has_unavailable_sensor = self._presence_snapshot()
        if has_unavailable_sensor and not is_anyone_present:
            self.log("Presence sensor unavailable; absence action deferred.", level="DEBUG")
            return

        if is_anyone_present:
            self._handle_presence()
            return

        self._handle_absence()

    def live_sync_handler(self, event_name: str, data: Dict[str, Any], kwargs: Dict[str, Any]) -> None:
        if data is not None and not isinstance(data, dict):
            self.log(f"Ignored {event_name}: invalid payload type", level="WARNING")
            return

        for target in self.target_entities:
            if target.startswith("light.") and self.get_state(target) == "on":
                self.log(f"Live sync applied: {target} (transition=2)", level="DEBUG")
                self.safe_turn_on(target, transition=2)

    def _handle_presence(self) -> None:
        if self.off_timer is not None:
            self.cancel_timer(self.off_timer, silent=True)
            self.off_timer = None
            self.log("Presence re-detected. Off-timer cancelled.", level="DEBUG")

        if self.sun_dependent and self.get_state("sun.sun") != "below_horizon":
            self.log("Sun is above horizon. Execution bypassed.", level="DEBUG")
            return

        for target in self.target_entities:
            self.safe_turn_on(target, **self.turn_on_kwargs)

    def _handle_absence(self) -> None:
        is_anyone_present, has_unavailable_sensor = self._presence_snapshot()
        if is_anyone_present:
            return

        if has_unavailable_sensor:
            self.log("Absence timer skipped due to unavailable presence sensor.", level="DEBUG")
            return

        current_delay = self.base_turn_off_delay
        if self.home_mode_entity and self.get_state(self.home_mode_entity) == "Comfort":
            current_delay = self.comfort_mode_delay

        if self.off_timer is not None:
            return

        if current_delay > 0:
            self.log(f"Absence confirmed. Initiating {current_delay}s delay sequence.")
            self.off_timer = self.run_in(self._turn_off_targets, current_delay)
            return

        self._turn_off_targets({})

    def _turn_off_targets(self, kwargs: Dict[str, Any]) -> None:
        self.off_timer = None

        if self.manual_mode and self.get_state(self.manual_mode) == "on":
            self.log("Turn-off dropped because manual mode is active.", level="DEBUG")
            return

        is_anyone_present, has_unavailable_sensor = self._presence_snapshot()
        if is_anyone_present or has_unavailable_sensor:
            self.log("Turn-off dropped after re-checking presence state.", level="DEBUG")
            return

        for target in self.target_entities:
            self.safe_turn_off(target, **self.turn_off_kwargs)
            self.call_service("homeassistant/update_entity", entity_id=target)

    def _presence_snapshot(self) -> tuple[bool, bool]:
        sensor_states = [self.get_state(sensor) for sensor in self.presence_sensors]
        is_anyone_present = any(state == "on" for state in sensor_states)
        has_unavailable_sensor = any(
            state is None or state in self._UNAVAILABLE_STATES for state in sensor_states
        )
        return is_anyone_present, has_unavailable_sensor
