from typing import Any, Dict, Optional

from base import SmartHomeBase


class NotificationEngine(SmartHomeBase):
    def initialize(self) -> None:
        super().initialize()

        self.default_notify_target: Optional[str] = self.args.get("default_notify_target")
        self.default_tts_player: Optional[str] = self.args.get("default_tts_player")
        self.tts_language: str = self.args.get("tts_language", "ko")
        self.quiet_start_hour: int = self.args.get("quiet_start_hour", 23)
        self.quiet_end_hour: int = self.args.get("quiet_end_hour", 7)

        self.listen_event(self.route_notification, "ROUTED_NOTIFY")

    def _is_quiet_hours(self) -> bool:
        current_hour = self.time().hour
        if self.quiet_start_hour > self.quiet_end_hour:
            return current_hour >= self.quiet_start_hour or current_hour < self.quiet_end_hour
        return self.quiet_start_hour <= current_hour < self.quiet_end_hour

    def route_notification(
        self,
        event_name: str,
        data: Dict[str, Any],
        kwargs: Dict[str, Any],
    ) -> None:
        if not isinstance(data, dict):
            return

        title = data.get("title", "Notification")
        message = data.get("message", "")
        level = data.get("level", "info")
        use_tts = bool(data.get("use_tts", False))
        extra_data = data.get("extra_data", {})
        is_quiet = self._is_quiet_hours()

        if self.default_notify_target and (level == "critical" or not is_quiet):
            notify_payload: Dict[str, Any] = {"title": title, "message": message}
            if isinstance(extra_data, dict) and extra_data:
                notify_payload["data"] = extra_data
            self.call_service(f"notify/{self.default_notify_target}", **notify_payload)

        if use_tts and self.default_tts_player and (level == "critical" or not is_quiet):
            self.call_service(
                "tts/speak",
                entity_id=self.default_tts_player,
                message=message,
                language=self.tts_language,
                cache=True,
            )
