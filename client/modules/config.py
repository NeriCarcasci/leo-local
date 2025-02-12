import json
import os
import typer
import questionary

# Define base directory for all CLI data
LEO_CLI_DIR = os.path.expanduser("~/.leo_cli")  # Now everything is under .leo_cli
CONFIG_FILE = os.path.join(LEO_CLI_DIR, "config.json")  # Config file path
SNAPSHOT_DIR = os.path.join(LEO_CLI_DIR, "snapshots")  # Directory for snapshots


class ConfigModule:
    DEFAULT_CONFIG = {
        "first_run": True,
        "execution_mode": "manual",
        "completion_installed": False,
        "logging": {
            "process": True,
            "run_cycle": True,
            "service": True,
            "config": True
        },
        "config_snapshot_in_run": False  # Whether to include config snapshot in each run log
    }

    def __init__(self):
        """Ensure .leo_cli exists, then load configuration from file or set defaults."""
        os.makedirs(LEO_CLI_DIR, exist_ok=True)  # Ensure base directory exists
        os.makedirs(SNAPSHOT_DIR, exist_ok=True)  # Ensure snapshot directory exists
        self.config = self._load_config()

    def _load_config(self):
        """Load or create the configuration file and ensure missing keys are added."""
        if not os.path.exists(CONFIG_FILE):
            self.config = self.DEFAULT_CONFIG  # Use defaults if no config file exists
            self.save_config()  # Ensure default config is saved
            return self.config

        try:
            with open(CONFIG_FILE, "r") as file:
                config_data = file.read().strip()  # Read content and remove extra spaces

            if not config_data:  # Handle empty file case
                raise ValueError("Config file is empty.")

            config = json.loads(config_data)  # Convert to dictionary

        except (json.JSONDecodeError, ValueError):
            typer.echo("⚠ Error: Config file is corrupted. Resetting to default settings.")
            config = self.DEFAULT_CONFIG
            self.save_config()

        # Ensure all default keys exist
        for key, default_value in self.DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = default_value

        # Ensure nested keys are also present
        if "logging" not in config:
            config["logging"] = self.DEFAULT_CONFIG["logging"]
        else:
            for log_type, enabled in self.DEFAULT_CONFIG["logging"].items():
                if log_type not in config["logging"]:
                    config["logging"][log_type] = enabled

        # Assign config and save any new changes
        self.config = config
        self.save_config()
        return self.config

    def save_config(self):
        """Save the current config to a file."""
        with open(CONFIG_FILE, "w") as file:
            json.dump(self.config, file, indent=4)

    def interactive_setup(self):
        """Interactive menu for modifying configuration settings."""
        while True:
            choice = questionary.select(
                "🔧 Configuration Menu: Use arrow keys to navigate, press Enter to modify.",
                choices=[
                    f"Execution Mode: {self.config['execution_mode']}",
                    "🔄 Toggle Logging Settings",
                    f"📁 Include Config Snapshot in Run Logs: {'Enabled' if self.config['config_snapshot_in_run'] else 'Disabled'}",
                    "📸 Save Configuration Snapshot",
                    "📂 Load Configuration Snapshot",
                    "Reset First Run Status",
                    "Exit Configuration"
                ]
            ).ask()

            if choice.startswith("Execution Mode"):
                self._change_execution_mode()
            elif choice == "🔄 Toggle Logging Settings":
                self._toggle_logging()
            elif choice == "📁 Include Config Snapshot in Run Logs":
                self._toggle_config_snapshot_in_run()
            elif choice == "📸 Save Configuration Snapshot":
                self._save_configuration_snapshot()
            elif choice == "📂 Load Configuration Snapshot":
                self._load_configuration_snapshot()
            elif choice == "Reset First Run Status":
                self._reset_first_run()
            elif choice == "Exit Configuration":
                typer.echo("✅ Configuration complete. Changes saved.")
                break

    def _change_execution_mode(self):
        """Change execution mode interactively."""
        mode = questionary.select(
            "Choose Execution Mode:",
            choices=["manual", "auto"]
        ).ask()

        if mode:
            self.config["execution_mode"] = mode
            self.save_config()
            typer.echo(f"✅ Execution mode set to: {mode}")

    def _toggle_logging(self):
        """Toggle logging settings interactively."""
        log_options = list(self.config["logging"].keys()) + ["Exit"]
        while True:
            choice = questionary.select(
                "📜 Toggle Log Types: (Enabled logs are shown, press Enter to toggle)",
                choices=[
                            f"{log_type.capitalize()} Logging: {'✅ Enabled' if self.config['logging'][log_type] else '❌ Disabled'}"
                            for log_type in self.config["logging"]
                        ] + ["Exit"]
            ).ask()

            if choice == "Exit":
                break

            log_type = choice.split(" ")[0].lower()
            self.config["logging"][log_type] = not self.config["logging"][log_type]
            self.save_config()
            typer.echo(
                f"🔄 {log_type.capitalize()} logging is now {'ENABLED' if self.config['logging'][log_type] else 'DISABLED'}.")

    def _toggle_config_snapshot_in_run(self):
        """Toggle whether configuration snapshots are included in run logs."""
        self.config["config_snapshot_in_run"] = not self.config["config_snapshot_in_run"]
        self.save_config()
        status = "ENABLED" if self.config["config_snapshot_in_run"] else "DISABLED"
        typer.echo(f"📁 Including Config Snapshot in Run Logs: {status}")

    def _save_configuration_snapshot(self):
        """Save the current configuration as a snapshot."""
        snapshot_name = f"config_snapshot_{typer.prompt('Enter a name for this snapshot')}.json"
        snapshot_path = os.path.join(SNAPSHOT_DIR, snapshot_name)

        with open(snapshot_path, "w") as file:
            json.dump(self.config, file, indent=4)

        typer.echo(f"📸 Configuration snapshot saved: {snapshot_path}")

    def _load_configuration_snapshot(self):
        """Load a saved configuration snapshot."""
        snapshots = os.listdir(SNAPSHOT_DIR)
        if not snapshots:
            typer.echo("⚠ No configuration snapshots available.")
            return

        choice = questionary.select(
            "📂 Select a snapshot to load:",
            choices=snapshots + ["Cancel"]
        ).ask()

        if choice == "Cancel":
            return

        snapshot_path = os.path.join(SNAPSHOT_DIR, choice)

        with open(snapshot_path, "r") as file:
            snapshot_data = json.load(file)

        # Ensure we don't override new settings if snapshots are outdated
        for key, value in snapshot_data.items():
            if key in self.config:
                self.config[key] = value

        self.save_config()
        typer.echo(f"✅ Loaded configuration snapshot: {choice}")

    def _reset_first_run(self):
        """Reset first run flag (useful for debugging)."""
        confirm = questionary.confirm("Are you sure you want to reset first-run status?").ask()
        if confirm:
            self.config["first_run"] = True
            self.save_config()
            typer.echo("🔄 First-run status reset. Next run will trigger setup.")
