import os
import json
import datetime
import logging
from pathlib import Path
from modules.config import ConfigModule  # Import ConfigModule to load logging flags

# Set base directory for logs under ~/.leo_cli
LEO_CLI_DIR = os.path.expanduser("~/.leo_cli")
LOG_DIR = os.path.join(LEO_CLI_DIR, "logs")
RUNS_DIR = os.path.join(LOG_DIR, "runs")
SNAPS_DIR = os.path.join(LOG_DIR, "snaps")


class LoggerModule:
    def __init__(self, config: ConfigModule = None):
        """Initialize logging system, loading log settings from configuration."""
        self.config = config or ConfigModule()  # Load config module
        self.LOG_TYPES = self.config.config.get("logging", {})  # Read log toggles

        # Ensure directories exist
        os.makedirs(RUNS_DIR, exist_ok=True)
        os.makedirs(SNAPS_DIR, exist_ok=True)

        # Setup logging
        self.logger = logging.getLogger("LEO Logger")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(os.path.join(LOG_DIR, "leo.log"))
        formatter = logging.Formatter("%(asctime)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log(self, log_type: str, code: str, message: str, status: str):
        """
        Log a message with a specific log type and status.

        Args:
            log_type (str): The category of the log (process, run_cycle, service, config).
            code (str): The unique log code identifier.
            message (str): The log message.
            status (str): SUCCESS or FAILURE.
        """
        # Check if log type is enabled in the config
        if not self.LOG_TYPES.get(log_type, False):
            return  # Skip logging if disabled

        log_entry = f"[{code}] - {message} - {status}"
        self.logger.info(log_entry)

        # If it's a run cycle log, save it in a dedicated file
        if log_type == "run_cycle":
            self._log_run_cycle(code, message, status)

    def _log_run_cycle(self, code: str, message: str, status: str):
        """Logs a run cycle event in a dedicated run file."""
        run_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        run_file = os.path.join(RUNS_DIR, f"RUN_{run_id}.log")

        with open(run_file, "a") as file:
            file.write(f"[{code}] - {message} - {status}\n")

    def log_process(self, code: str, message: str, status: str = "SUCCESS"):
        """Log process-related events."""
        self.log("process", code, message, status)

    def log_run_cycle(self, code: str, message: str, status: str = "SUCCESS"):
        """Log execution cycle events."""
        self.log("run_cycle", code, message, status)

    def log_service(self, code: str, message: str, status: str = "SUCCESS"):
        """Log external API and service interactions."""
        self.log("service", code, message, status)

    def log_config(self, code: str, message: str, status: str = "SUCCESS"):
        """Log configuration changes and snapshots."""
        self.log("config", code, message, status)

    def save_configuration_snapshot(self):
        """Save a configuration snapshot to a JSON file."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        snapshot_file = os.path.join(SNAPS_DIR, f"config_snapshot_{timestamp}.json")

        with open(snapshot_file, "w") as file:
            json.dump(self.config.config, file, indent=4)

        self.log_config("CFG00", f"Configuration snapshot saved: {snapshot_file}")


