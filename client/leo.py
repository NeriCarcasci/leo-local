import os
import subprocess
import sys
from modules.executor import CommandExecutionModule
from modules.logger import LoggerModule
from modules.secrets import SecretsModule
from modules.config import ConfigModule

def check_and_install_dependencies():
    """Check if LEO is fully set up; if not, run `install.py`."""
    try:
        import typer
        import questionary
    except ImportError:
        print("🔹 Dependencies not found. Installing them now...")
        subprocess.run([sys.executable, "install.py"], check=True)

class LeoCLI:
    def __init__(
        self,
        executor: CommandExecutionModule = None,
        logger: LoggerModule = None,
        secrets: SecretsModule = None,
        config: ConfigModule = None
    ):
        """CLI Application for LEO with dependency injection."""
        self.app = typer.Typer(help="LEO - AI-powered CLI Assistant 🚀")

        # Inject dependencies (use default implementations if not provided)
        self.executor = executor or CommandExecutionModule()
        self.logger = logger or LoggerModule()
        self.secrets = secrets or SecretsModule()
        self.config = config or ConfigModule()

        # Register CLI commands
        self.app.command(help="Execute a command via LEO's AI-powered CLI")(self.execute)
        self.app.command(help="Modify execution settings interactively")(self.configure)

    def execute(self, command: str, auto: bool = typer.Option(None, help="Run in autonomous mode (overrides config)")):
        """Execute a system command, automatically handling sensitive data."""
        
        sanitized_command = self.secrets.sanitize_command(command)
        execution_mode = auto if auto is not None else self.config.config.get("execution_mode", "manual")

        if execution_mode == "manual":
            typer.confirm(f"Execute: {sanitized_command}?", abort=True)

        result = self.executor.execute_command(sanitized_command)
        self.logger.log_execution(sanitized_command, result)
        typer.echo(f"Result: {result}")

    def configure(self):
        """Open the interactive configuration menu."""
        self.config.interactive_setup()

def main():
    """Entry point for the CLI."""
    check_and_install_dependencies()
    cli = LeoCLI()  # Instantiate with default modules
    cli.app()

if __name__ == "__main__":
    main()