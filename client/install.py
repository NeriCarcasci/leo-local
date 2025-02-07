import os
import sys
import platform
import subprocess
import json
import importlib.util

CONFIG_DIR = os.path.expanduser("~/.leo_cli")
VENV_DIR = os.path.join(CONFIG_DIR, "venv")
VENV_PYTHON = os.path.join(VENV_DIR, "bin", "python3") if platform.system() != "Windows" else os.path.join(VENV_DIR, "Scripts", "python.exe")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def is_running_inside_venv():
    """Check if the script is currently running inside the virtual environment."""
    return sys.prefix == VENV_DIR

def create_virtualenv():
    """Create a virtual environment for LEO CLI if it doesn't exist."""
    if not os.path.exists(VENV_DIR):
        print("🔹 Creating a virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", VENV_DIR], check=True)

def restart_in_venv():
    """Restart the script inside the virtual environment if it's not already inside."""
    if not is_running_inside_venv():
        print("🔹 Restarting inside virtual environment...")
        os.execv(VENV_PYTHON, [VENV_PYTHON] + sys.argv)

def install_dependencies():
    """Install all required dependencies inside the virtual environment."""
    pip_executable = os.path.join(VENV_DIR, "bin", "pip") if platform.system() != "Windows" else os.path.join(VENV_DIR, "Scripts", "pip.exe")

    # Ensure pip is up to date
    subprocess.run([pip_executable, "install", "--upgrade", "pip"], check=True)

    # Install requirements
    print("🔹 Installing dependencies inside virtual environment...")
    subprocess.run([pip_executable, "install", "-r", "requirements.txt"], check=True)
    print("✅ Dependencies installed.")

def install_questionary():
    """Ensure `questionary` is available inside the virtual environment."""
    pip_executable = os.path.join(VENV_DIR, "bin", "pip") if platform.system() != "Windows" else os.path.join(VENV_DIR, "Scripts", "pip.exe")

    if importlib.util.find_spec("questionary") is None:
        print("🔹 `questionary` not found. Installing it inside the virtual environment...")
        subprocess.run([pip_executable, "install", "questionary"], check=True)
        print("✅ Installed `questionary` inside virtual environment.")

def detect_and_store_os():
    """Detect the OS and store it in the config file."""
    detected_os = platform.system()
    config_data = {"os": detected_os}

    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w") as file:
        json.dump(config_data, file, indent=4)

    print(f"✅ OS detected: {detected_os}. Stored in {CONFIG_FILE}")

if __name__ == "__main__":
    print("🚀 Setting up LEO CLI...")

    create_virtualenv()
    restart_in_venv()  # Ensure we are inside the virtual environment before proceeding
    install_dependencies()
    install_questionary()
    detect_and_store_os()

    print("🎉 LEO CLI is ready! Use `source ~/.leo_cli/venv/bin/activate` to start using it.")