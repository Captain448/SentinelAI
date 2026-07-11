import sys
import logging
from app.core.config import settings

# Configure logging
log_level_map = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
current_level = log_level_map.get(settings.LOG_LEVEL.upper(), logging.INFO)

# Define custom formatting that makes it clean and easy to scan
logging.basicConfig(
    level=current_level,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("sentinel")


# Helper agent logging functions to enforce exact formatting from specifications
def log_agent(agent_name: str, message: str) -> None:
    """Prints a clean logs formatted precisely as required by specifications:

    e.g., [VisionAgent] Entity detected.
    """
    # Print directly to stdout for cleaner presentation matching specifications
    print(f"[{agent_name}] {message}", flush=True)
    # Also log to system logs
    logger.info(f"[{agent_name}] {message}")
