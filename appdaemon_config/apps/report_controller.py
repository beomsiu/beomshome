import datetime
from typing import Any, Dict

from base import SmartHomeBase


class EnergyReportController(SmartHomeBase):
    def initialize(self) -> None:
        super().initialize()

        self.report_time: str = self.args.get("report_time", "09:00:00")
        self.report_day: int = self.args.get("report_day", 0)

        self.status_sensor: str = self.args.get("status_sensor", "")
        self.my_energy_sensor: str = self.args.get("my_energy_sensor", "")
        self.avg_energy_sensor: str = self.args.get("avg_energy_sensor", "")
        self.fee_sensor: str = self.args.get("fee_sensor", "")

        try:
            time_obj = datetime.datetime.strptime(self.report_time, "%H:%M:%S").time()
        except ValueError:
            self.log(f"Invalid report_time format: {self.report_time}", level="ERROR")
            return

        self.run_daily(self.generate_report, time_obj)

    def generate_report(self, kwargs: Dict[str, Any]) -> None:
        if self.datetime().weekday() != self.report_day:
            return

        status = self.get_state(self.status_sensor) if self.status_sensor else "unknown"
        my_energy = self.get_state(self.my_energy_sensor) if self.my_energy_sensor else "unknown"
        avg_energy = self.get_state(self.avg_energy_sensor) if self.avg_energy_sensor else "unknown"
        fee = self.get_state(self.fee_sensor) if self.fee_sensor else "unknown"

        message = (
            f"Status: {status}\n"
            f"My Home: {my_energy} kWh\n"
            f"Complex Avg: {avg_energy} kWh\n"
            f"Estimated Fee: {fee} KRW"
        )

        self.send_notification(
            title="Weekly Energy Report",
            message=message,
            level="info",
            extra_data={"clickAction": "/energy", "group": "energy-reports"},
        )
