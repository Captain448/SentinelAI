import copy
from typing import List, Dict, Any
from app.core.shared_memory import SharedMemory
from app.core.logger import logger


class StateMachine:
    """Manages system state transitions, holds the current active SharedMemory,

    creates snapshots, and stores audit logs.
    """

    def __init__(self):
        self.state: SharedMemory = SharedMemory()
        self.snapshots: List[Dict[str, Any]] = []
        self.audit_logs: List[Dict[str, Any]] = []

    def update_state(self, key_path: str, value: Any, actor: str = "System") -> None:
        """Dynamically updates a value in SharedMemory, logs it, and creates an audit entry."""
        keys = key_path.split(".")
        current = self.state

        # Traverse to the second to last attribute
        for key in keys[:-1]:
            if hasattr(current, key):
                current = getattr(current, key)
            else:
                logger.error(f"Invalid path in shared memory: {key_path}")
                return

        last_key = keys[-1]
        if hasattr(current, last_key):
            old_val = getattr(current, last_key)
            setattr(current, last_key, value)
            # Log transition
            audit_entry = {
                "timestamp": self.state.tracked_entity.timestamp,
                "actor": actor,
                "field": key_path,
                "old_value": copy.deepcopy(old_val),
                "new_value": copy.deepcopy(value)
            }
            self.audit_logs.append(audit_entry)
            logger.debug(f"[{actor}] Updated {key_path} from {old_val} to {value}")
        else:
            logger.error(f"Field {last_key} does not exist in target model at path {key_path}")

    def create_snapshot(self, event_description: str) -> None:
        """Takes a copy of the current state and logs the transition snapshot."""
        snapshot = {
            "event": event_description,
            "timestamp": self.state.tracked_entity.timestamp,
            "state": self.state.to_dict()
        }
        self.snapshots.append(snapshot)
        logger.debug(f"State snapshot recorded for event: {event_description}")

    def get_snapshot_history(self) -> List[Dict[str, Any]]:
        return self.snapshots

    def get_audit_logs(self) -> List[Dict[str, Any]]:
        return self.audit_logs

    def reset(self) -> None:
        """Resets the state machine to default empty states."""
        self.state = SharedMemory()
        self.snapshots = []
        self.audit_logs = []
