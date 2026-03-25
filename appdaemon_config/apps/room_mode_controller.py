import datetime
from typing import Any, Dict, List, Optional

from base import SmartHomeBase


class SleepModeController(SmartHomeBase):
    def initialize(self) -> None:
        super().initialize()

        self.sleep_boolean: str = self.args.get("sleep_boolean", "")
        self.wakeup_time_entity: str = self.args.get("wakeup_time_entity", "")
        self.lights: List[str] = self.args.get("lights", [])
        self.manual_mode_boolean: Optional[str] = self.args.get("manual_mode_boolean")

        self.media_player: Optional[str] = self.args.get("media_player")
        self.notify_target: Optional[str] = self.args.get("notify_target")
        self.weather_entity: str = self.args.get("weather_entity", "weather.forecast_home")

        self.wakeup_timer: Optional[str] = None
        self._suppress_manual_off: bool = False

        if not self.sleep_boolean or not self.wakeup_time_entity:
            self.log("sleep_boolean and wakeup_time_entity are required", level="ERROR")
            return

        self.listen_state(self.sleep_mode_changed, self.sleep_boolean, attribute="all")
        self.listen_state(self.wakeup_time_changed, self.wakeup_time_entity)

        self._schedule_wakeup()

    def sleep_mode_changed(
        self,
        entity: str,
        attribute: str,
        old: Dict[str, Any],
        new: Dict[str, Any],
        kwargs: Dict[str, Any],
    ) -> None:
        if not isinstance(new, dict):
            return

        old_state = old.get("state") if isinstance(old, dict) else None
        new_state = new.get("state")
        if new_state == old_state:
            return

        if new_state == "on":
            self._execute_sleep_sequence()
            return

        if new_state == "off":
            if self._suppress_manual_off:
                return

            context = new.get("context")
            if not isinstance(context, dict):
                return

            if context.get("parent_id") is None and context.get("user_id") is not None:
                self._execute_manual_wakeup_sequence()

    def _execute_sleep_sequence(self) -> None:
        for light in self.lights:
            self.safe_turn_off(light, transition=3)

        self._notify(message="Sleep mode has been enabled.")

        tts_msg = "Sleep mode has been enabled. Good night."
        time_str = self.get_state(self.wakeup_time_entity)
        if isinstance(time_str, str) and time_str and time_str not in self._UNAVAILABLE_STATES:
            try:
                parsed_time = self._parse_time(time_str)
                tts_msg = (
                    "Sleep mode has been enabled. "
                    f"Wake-up time is {parsed_time.hour:02d}:{parsed_time.minute:02d}. Good night."
                )
            except ValueError:
                pass

        self._tts(tts_msg)

    def _schedule_wakeup(self) -> None:
        if self.wakeup_timer is not None:
            self.cancel_timer(self.wakeup_timer, silent=True)
            self.wakeup_timer = None

        time_str = self.get_state(self.wakeup_time_entity)
        if not isinstance(time_str, str) or not time_str or time_str in self._UNAVAILABLE_STATES:
            return

        try:
            time_obj = self._parse_time(time_str)
        except ValueError:
            self.log(f"Invalid wakeup time format: {time_str}", level="ERROR")
            return

        self.wakeup_timer = self.run_daily(self._execute_scheduled_wakeup, time_obj)
        self.log(f"Wake-up schedule registered at {time_obj.strftime('%H:%M:%S')}.")

    def wakeup_time_changed(
        self,
        entity: str,
        attribute: str,
        old: str,
        new: str,
        kwargs: Dict[str, Any],
    ) -> None:
        if new == old:
            return
        self._schedule_wakeup()

    def _execute_scheduled_wakeup(self, kwargs: Dict[str, Any]) -> None:
        if self.get_state(self.sleep_boolean) != "on":
            return

        self.log("Scheduled wake-up sequence started.", level="INFO")

        if self.manual_mode_boolean:
            self.safe_turn_off(self.manual_mode_boolean)

        self._suppress_manual_off = True
        try:
            self.safe_turn_off(self.sleep_boolean)
        finally:
            self._suppress_manual_off = False

        for light in self.lights:
            self.safe_turn_on(
                light,
                transition=10,
                color_temp_kelvin=6500,
                brightness_pct=100,
            )

        self._tts("Wake-up time. Please start your day.")

        weather_state = self.get_state(self.weather_entity)
        temperature = self.get_state(self.weather_entity, attribute="temperature")
        humidity = self.get_state(self.weather_entity, attribute="humidity")

        self._notify(
            title="Good morning",
            message=(
                "Scheduled wake-up completed and sleep mode was disabled. "
                f"Weather: {weather_state}, temperature: {temperature}, humidity: {humidity}."
            ),
        )

    def _execute_manual_wakeup_sequence(self) -> None:
        self.log("Sleep mode manually disabled by user.", level="INFO")
        self._notify(message="Sleep mode has been disabled.")
        for light in self.lights:
            self.safe_turn_on(light, transition=3)

    def _notify(self, message: str, title: Optional[str] = None) -> None:
        if not self.notify_target:
            return

        payload: Dict[str, Any] = {"message": message}
        if title:
            payload["title"] = title

        self.call_service(f"notify/{self.notify_target}", **payload)

    def _tts(self, message: str) -> None:
        if not self.media_player:
            return

        self.call_service(
            "tts/speak",
            entity_id=self.media_player,
            message=message,
            language="ko",
            cache=True,
        )

    def _parse_time(self, value: str) -> datetime.time:
        time_formats = ["%H:%M:%S", "%H:%M"]
        for fmt in time_formats:
            try:
                return datetime.datetime.strptime(value, fmt).time()
            except ValueError:
                continue

        raise ValueError(value)
