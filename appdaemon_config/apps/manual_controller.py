from typing import Any, Dict, List, Optional

from base import SmartHomeBase


class ManualModeController(SmartHomeBase):
    def initialize(self) -> None:
        super().initialize()

        self.switches: List[str] = self.args.get("switches", [])
        self.manual_boolean: Optional[str] = self.args.get("manual_boolean")

        self.default_duration: int = self.args.get("default_duration", 1200)
        self.night_duration: Optional[int] = self.args.get("night_duration")
        self.night_start_hour: int = self.args.get("night_start_hour", 23)
        self.night_end_hour: int = self.args.get("night_end_hour", 7)

        self.reset_sensor: Optional[str] = self.args.get("reset_sensor")
        self.reset_sensor_delay: int = self.args.get("reset_sensor_delay", 300)
        self.sync_switch: Optional[str] = self.args.get("sync_switch")

        self.timer_handle: Optional[str] = None
        self.timer_generation: int = 0

        if not self.manual_boolean:
            self.log("manual_boolean is required for ManualModeController", level="ERROR")
            return

        for switch in self.switches:
            self.listen_state(self.switch_toggled, switch, attribute="all")

        if self.reset_sensor:
            self.listen_state(
                self.sensor_reset_triggered,
                self.reset_sensor,
                new="off",
                duration=self.reset_sensor_delay,
            )

        if self.sync_switch:
            self.listen_state(self.sync_switch_handler, self.manual_boolean)

        self.listen_state(self.manual_boolean_turned_on, self.manual_boolean, new="on")

        current_manual_state = self.get_state(self.manual_boolean)
        if current_manual_state == "on":
            self._start_or_restart_timer()
            if self.sync_switch:
                self.safe_turn_off(self.sync_switch)
        elif current_manual_state == "off" and self.sync_switch:
            self.safe_turn_on(self.sync_switch)

    def switch_toggled(
        self,
        entity: str,
        attribute: str,
        old: Dict[str, Any],
        new: Dict[str, Any],
        kwargs: Dict[str, Any],
    ) -> None:
        if not new or not old:
            return

        if self.sync_switch and entity == self.sync_switch:
            return

        old_state = old.get("state")
        new_state = new.get("state")
        if new_state is None or new_state in self._UNAVAILABLE_STATES:
            return

        if old_state == new_state:
            return

        if not self._is_physical_interaction(new):
            return

        self.log(f"Physical interaction detected on {entity}. Activating Manual Mode.", level="INFO")
        self._activate_manual_mode()

    def _activate_manual_mode(self) -> None:
        if not self.manual_boolean:
            return

        self.safe_turn_on(self.manual_boolean)

        self._start_or_restart_timer()

    def _start_or_restart_timer(self) -> None:
        if not self.manual_boolean:
            return

        if self.timer_handle is not None:
            self.cancel_timer(self.timer_handle, silent=True)
            self.timer_handle = None

        self.timer_generation += 1
        duration = self.default_duration
        if self.night_duration:
            current_hour = self.time().hour
            if current_hour >= self.night_start_hour or current_hour < self.night_end_hour:
                duration = self.night_duration
                self.log("Night time detected. Applying shorter manual mode duration.", level="DEBUG")

        self.log(f"Manual mode timer started for {duration} seconds.")
        self.timer_handle = self.run_in(
            self._deactivate_manual_mode,
            duration,
            generation=self.timer_generation,
        )

    def sensor_reset_triggered(
        self,
        entity: str,
        attribute: str,
        old: str,
        new: str,
        kwargs: Dict[str, Any],
    ) -> None:
        if not self.manual_boolean:
            return

        if self.get_state(self.manual_boolean) == "on":
            self.log(f"Reset sensor {entity} triggered early reset. Deactivating Manual Mode.", level="INFO")
            self._deactivate_manual_mode({})

    def _deactivate_manual_mode(self, kwargs: Dict[str, Any]) -> None:
        scheduled_generation = kwargs.get("generation") if isinstance(kwargs, dict) else None
        if scheduled_generation is not None and scheduled_generation != self.timer_generation:
            return

        self.timer_handle = None

        if self.manual_boolean:
            self.safe_turn_off(self.manual_boolean)

        self.log("Manual Mode deactivated.", level="INFO")

    def sync_switch_handler(
        self,
        entity: str,
        attribute: str,
        old: str,
        new: str,
        kwargs: Dict[str, Any],
    ) -> None:
        if not self.sync_switch:
            return

        if new == "on":
            self.safe_turn_off(self.sync_switch)
            return

        if new == "off":
            self.safe_turn_on(self.sync_switch)

    def manual_boolean_turned_on(
        self,
        entity: str,
        attribute: str,
        old: str,
        new: str,
        kwargs: Dict[str, Any],
    ) -> None:
        if old == "on":
            return

        self._start_or_restart_timer()

    def _is_physical_interaction(self, state_payload: Dict[str, Any]) -> bool:
        context = state_payload.get("context")
        if not isinstance(context, dict):
            return False

        user_id = context.get("user_id")
        parent_id = context.get("parent_id")
        return user_id is None and parent_id is None
