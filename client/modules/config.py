import json
import os
import typer
import questionary

CONFIG_FILE = os.path.expanduser("~/.leo_config.json")  # Store config in user home

class ConfigModule:
    def __init__(self):
        """Load configuration from file or set defaults."""
        self.config = self._load_config()

    def _load_config(self):
        """Load or create the configuration file."""
        if not os.path.exists(CONFIG_FILE):
            return {
                "first_run": True,
                "execution_mode": "manual",
                "completion_installed": False
            }
        
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)

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
                    "Reset First Run Status",
                    "Exit Configuration"
                ]
            ).ask()

            if choice.startswith("Execution Mode"):
                self._change_execution_mode()
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

    def _reset_first_run(self):
        """Reset first run flag (useful for debugging)."""
        confirm = questionary.confirm("Are you sure you want to reset first-run status?").ask()
        if confirm:
            self.config["first_run"] = True
            self.save_config()
            typer.echo("🔄 First-run status reset. Next run will trigger setup.")