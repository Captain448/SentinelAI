import datetime
from typing import Callable, List, Dict, Any


class SimulatedClock:
    """Manages virtual timeline progression and tracks scheduled timed events."""

    def __init__(self, start_time_str: str = "00:00"):
        self.fmt = "%H:%M"
        self.current_time = datetime.datetime.strptime(start_time_str, self.fmt)
        self.scheduled_events: List[Dict[str, Any]] = []

    def advance_time(self, minutes: int) -> str:
        """Increments the virtual clock by a specific number of minutes."""
        self.current_time += datetime.timedelta(minutes=minutes)
        return self.get_time_string()

    def get_time_string(self) -> str:
        """Returns string representation of current virtual time."""
        return self.current_time.strftime(self.fmt)

    def schedule_event(self, delay_minutes: int, callback: Callable, *args, **kwargs) -> None:
        """Schedules a callback event after a virtual delay."""
        trigger_time = self.current_time + datetime.timedelta(minutes=delay_minutes)
        self.scheduled_events.append({
            "trigger_time": trigger_time,
            "callback": callback,
            "args": args,
            "kwargs": kwargs,
            "fired": False
        )

    def tick(self) -> None:
        """Checks and runs any events scheduled for trigger before or at current time."""
        for event in self.scheduled_events:
            if not event["fired"] and self.current_time >= event["trigger_time"]:
                event["fired"] = True
                event["callback"](*event["args"], **event["kwargs"])
