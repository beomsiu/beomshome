from typing import Any, Dict, List, Optional, Tuple

from base import SmartHomeBase


class AwayModeController(SmartHomeBase):
    def initialize(self) -> None:
        super().initialize()

        self.people: List[str] = self.args.get("people", [])
        self.away_mode_boolean: str = self.args.get("away_mode_boolean", "")
        self.notification_target: Optional[str] = self.args.get("notification_target")
        self.away_delay: int = self.args.get("away_delay", 300)

        self.away_timer: Optional[str] = None
        self.away_generation: int = 0

        if not self.away_mode_boolean:
            self.log("away_mode_boolean is required for AwayModeController", level="ERROR")
            return

        for person in self.people:
            self.listen_state(self.location_changed, person)

    def location_changed(
        self,
        entity: str,
        attribute: str,
        old: str,
        new: str,
        kwargs: Dict[str, Any],
    ) -> None:
        if new is None or new in self._UNAVAILABLE_STATES:
            if self.away_timer is not None:
                self.cancel_timer(self.away_timer, silent=True)
                self.away_timer = None
                self.away_generation += 1
                self.log("Away timer canceled due to unavailable/unknown state.", level="DEBUG")
            return

        all_away, has_unknown = self._away_snapshot()
        current_away_state = self.get_state(self.away_mode_boolean)

        if has_unknown:
            if self.away_timer is not None:
                self.cancel_timer(self.away_timer, silent=True)
                self.away_timer = None
                self.away_generation += 1
                self.log("Away timer canceled due to unknown person state.", level="DEBUG")
            return

        if all_away and current_away_state == "off":
            if self.away_timer is None:
                self.away_generation += 1
                self.log(
                    f"All people away detected. Activating away mode in {self.away_delay} seconds."
                )
                self.away_timer = self.run_in(
                    self.activate_away_mode,
                    self.away_delay,
                    generation=self.away_generation,
                )
            return

        if self.away_timer is not None:
            self.cancel_timer(self.away_timer, silent=True)
            self.away_timer = None
            self.log("Away activation canceled because someone returned.", level="INFO")

        if not all_away and current_away_state == "on":
            self.deactivate_away_mode()

    def activate_away_mode(self, kwargs: Dict[str, Any]) -> None:
        scheduled_generation = kwargs.get("generation") if isinstance(kwargs, dict) else None
        if scheduled_generation is not None and scheduled_generation != self.away_generation:
            return

        self.away_timer = None

        all_away, has_unknown = self._away_snapshot()
        if has_unknown or not all_away:
            return

        self.safe_turn_on(self.away_mode_boolean)
        self._notify(
            title="Family away",
            message="All family members are away. Away mode was enabled.",
        )
        self.log("Away mode activated.", level="INFO")

    def deactivate_away_mode(self) -> None:
        self.safe_turn_off(self.away_mode_boolean)
        self._notify(
            title="Family arrival",
            message="A family member arrived home. Away mode was disabled.",
        )
        self.log("Away mode deactivated.", level="INFO")

    def _away_snapshot(self) -> Tuple[bool, bool]:
        states = [self.get_state(person) for person in self.people]
        has_unknown = any(state is None or state in self._UNAVAILABLE_STATES for state in states)
        all_away = all(state == "not_home" for state in states) if states else False
        return all_away, has_unknown

    def _notify(self, title: str, message: str) -> None:
        if not self.notification_target:
            return

        self.call_service(
            f"notify/{self.notification_target}",
            title=title,
            message=message,
        )


class GlobalLightSyncController(SmartHomeBase):
    def initialize(self) -> None:
        super().initialize()
        self.sliders: List[str] = self.args.get("sliders", [])
        for slider in self.sliders:
            self.listen_state(self.slider_changed, slider)

    def slider_changed(
        self,
        entity: str,
        attribute: str,
        old: str,
        new: str,
        kwargs: Dict[str, Any],
    ) -> None:
        if new == old or new in self._UNAVAILABLE_STATES:
            return

        self.log(f"Global sync triggered by {entity} -> {new}", level="DEBUG")
        self.fire_event("GLOBAL_LIGHT_SYNC")


class EntranceSecurityController(SmartHomeBase):
    def initialize(self) -> None:
        super().initialize()

        self.door_sensor: str = self.args.get("door_sensor", "")
        self.presence_sensor: str = self.args.get("presence_sensor", "")
        self.welcome_lights: List[str] = self.args.get("welcome_lights", [])
        self.alert_lights: List[str] = self.args.get("alert_lights", [])
        self.media_player: Optional[str] = self.args.get("media_player")
        self.notify_target: Optional[str] = self.args.get("notify_target")

        self.alert_timer: Optional[str] = None
        self.welcome_off_timer: Optional[str] = None

        if not self.door_sensor:
            self.log("door_sensor is required for EntranceSecurityController", level="ERROR")
            return

        self.listen_state(self.door_state_changed, self.door_sensor)

    def door_state_changed(
        self,
        entity: str,
        attribute: str,
        old: str,
        new: str,
        kwargs: Dict[str, Any],
    ) -> None:
        if new == "on":
            self._handle_door_open()
            return

        if new == "off":
            self._handle_door_closed()

    def _handle_door_open(self) -> None:
        self.log("Door opened. Starting welcome and monitoring sequences.", level="INFO")

        for light in self.welcome_lights:
            self.safe_turn_on(light)

        self._notify("Entrance door opened.", title="Entrance event")

        if self.welcome_off_timer is not None:
            self.cancel_timer(self.welcome_off_timer, silent=True)
            self.welcome_off_timer = None

        if self.alert_timer is not None:
            self.cancel_timer(self.alert_timer, silent=True)
            self.alert_timer = None

        self.alert_timer = self.run_in(self._trigger_warning, 60)

    def _handle_door_closed(self) -> None:
        self.log("Door closed. Stopping alerts and scheduling cleanup.", level="INFO")

        if self.alert_timer is not None:
            self.cancel_timer(self.alert_timer, silent=True)
            self.alert_timer = None

        self._notify("Entrance door closed.")

        if self.media_player:
            self.call_service("media_player/media_stop", entity_id=self.media_player)

        for light in self.alert_lights:
            self.safe_turn_on(light, color_temp_kelvin=6500, brightness_pct=100)

        self.welcome_off_timer = self.run_in(self._welcome_off_check, 180)

    def _trigger_warning(self, kwargs: Dict[str, Any]) -> None:
        self.alert_timer = None
        if self.get_state(self.door_sensor) != "on":
            return

        self.log("Door remains open. Sending high-priority alert.", level="WARNING")
        self._notify(
            "Door has been open for over 1 minute. Please check entrance.",
            title="Door open alert",
            data={"priority": "high", "ttl": 0},
        )

        if self.media_player:
            self.call_service("media_player/volume_set", entity_id=self.media_player, volume_level=0.6)
            self.call_service(
                "tts/speak",
                entity_id=self.media_player,
                message="Alert. The entrance door is still open.",
                language="ko",
                cache=True,
            )

        for light in self.alert_lights:
            self.safe_turn_on(light, brightness_pct=100, rgb_color=[255, 0, 0])

        self.alert_timer = self.run_in(self._trigger_warning, 10)

    def _welcome_off_check(self, kwargs: Dict[str, Any]) -> None:
        self.welcome_off_timer = None
        if not self.presence_sensor:
            for light in self.welcome_lights:
                self.safe_turn_off(light)
            return

        if self.get_state(self.presence_sensor) == "off":
            for light in self.welcome_lights:
                self.safe_turn_off(light)

    def _notify(self, message: str, title: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> None:
        if not self.notify_target:
            return

        payload: Dict[str, Any] = {"message": message}
        if title:
            payload["title"] = title
        if data:
            payload["data"] = data

        self.call_service(f"notify/{self.notify_target}", **payload)
