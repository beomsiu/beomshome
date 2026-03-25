import importlib
from typing import Any, Dict, Optional

hass = importlib.import_module("hassapi")


class SmartHomeBase(hass.Hass):
    """
    Core base class for Smart Home AppDaemon modules.
    Provides safe execution wrappers, auditable logging, and cascading profile resolution.
    """

    _UNAVAILABLE_STATES = {"unknown", "unavailable"}

    def initialize(self) -> None:
        self.tag = self.args.get("app_name", self.__class__.__name__)
        self.log(f"[{self.tag}] Initialized", level="INFO")

    def _resolve_light_profile(self, custom_kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve lighting params using 3-tier cascading architecture:
        tier1(global UI) -> tier2(room config) -> tier3(execution args)
        """
        final_profile: Dict[str, Any] = {}

        global_brightness = self.get_state("input_number.global_brightness")
        if global_brightness and global_brightness not in self._UNAVAILABLE_STATES:
            try:
                final_profile["brightness_pct"] = int(float(global_brightness))
            except (TypeError, ValueError):
                self.log(
                    f"Invalid cast for global_brightness: {global_brightness}",
                    level="WARNING",
                )

        global_color_temp = self.get_state("input_number.global_color_temp")
        if global_color_temp and global_color_temp not in self._UNAVAILABLE_STATES:
            try:
                final_profile["color_temp_kelvin"] = int(float(global_color_temp))
            except (TypeError, ValueError):
                self.log(
                    f"Invalid cast for global_color_temp: {global_color_temp}",
                    level="WARNING",
                )

        room_profile = self.args.get("room_light_profile", {})
        if isinstance(room_profile, dict):
            final_profile.update(room_profile)

        final_profile.update(custom_kwargs)

        if "transition" not in final_profile:
            final_profile["transition"] = 3

        return final_profile

    def safe_turn_on(self, entity_id: str, **kwargs: Any) -> None:
        """Safely turn on an entity and inject light profile for light domain."""
        current_state = self.get_state(entity_id)
        if current_state is not None and current_state not in self._UNAVAILABLE_STATES:
            if entity_id.startswith("light."):
                final_params = self._resolve_light_profile(kwargs)
                self.turn_on(entity_id, **final_params)
                self.log(
                    f"ACTION: {entity_id} ON with profile {final_params}",
                    level="DEBUG",
                )
            else:
                self.turn_on(entity_id, **kwargs)
                self.log(
                    f"ACTION: {entity_id} ON with params {kwargs}",
                    level="DEBUG",
                )
            return

        self.log(
            f"WARNING: {entity_id} is unavailable/unknown. Command dropped.",
            level="WARNING",
        )

    def safe_turn_off(self, entity_id: str, **kwargs: Any) -> None:
        """Safely turn off an entity."""
        current_state = self.get_state(entity_id)
        if current_state is not None and current_state not in self._UNAVAILABLE_STATES:
            self.turn_off(entity_id, **kwargs)
            self.log(f"ACTION: {entity_id} OFF", level="DEBUG")
            return

        self.log(
            f"WARNING: {entity_id} is unavailable/unknown. Command dropped.",
            level="WARNING",
        )

    def send_notification(
        self,
        title: str,
        message: str,
        level: str = "info",
        use_tts: bool = False,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        payload = {
            "title": title,
            "message": message,
            "level": level,
            "use_tts": use_tts,
            "source_app": self.tag,
            "extra_data": extra_data or {},
        }
        self.fire_event("ROUTED_NOTIFY", **payload)
        self.log(f"Notification event fired: [{level.upper()}] {title}", level="DEBUG")
