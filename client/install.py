import os
import sys
import platform
import subprocess
import json
import shutil
import ctypes  # Used for checking admin privileges on Windows
import argparse  # For handling command-line flags

CONFIG_DIR = os.path.expanduser("~/.leo_cli")
VENV_DIR = os.path.join(CONFIG_DIR, "venv")
BIN_DIR = os.path.join(CONFIG_DIR, "bin")
FLAGS_FILE = os.path.join(CONFIG_DIR, "install_flags.json")
LEO_SCRIPT_WIN = os.path.join(BIN_DIR, "leo.cmd")
LEO_SCRIPT_LINUX = os.path.join(BIN_DIR, "leo")
VENV_PYTHON = os.path.join(VENV_DIR, "bin", "python") if platform.system() != "Windows" else os.path.join(VENV_DIR, "Scripts", "python.exe")

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--loud", action="store_true", help="Show full installation output")
args = parser.parse_args()

def run_command(command, hide_output=True, shell=False):
    """Run a command silently unless --loud flag is used."""
    if args.loud:
        subprocess.run(command, check=True, shell=shell)
    else:
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=shell)

def is_admin():
    """Check if script is running with administrator privileges (Windows only)."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def load_flags():
    """Load the installation flags to check completed steps."""
    if os.path.exists(FLAGS_FILE):
        with open(FLAGS_FILE, "r") as file:
            return json.load(file)
    return {}


def save_flags(flags):
    """Save updated installation flags."""
    with open(FLAGS_FILE, "w") as file:
        json.dump(flags, file, indent=4)



def create_virtualenv():
    """Create a virtual environment if it doesn’t exist."""
    flags = load_flags()
    if flags.get("venv_created"):
        print("✅ Virtual environment already exists. Skipping...")
        return

    print("🔹 Creating virtual environment...")
    run_command([sys.executable, "-m", "venv", VENV_DIR])
    flags["venv_created"] = True
    save_flags(flags)


def create_executable():
    """Create a global 'leo' command that always runs inside venv."""
    flags = load_flags()
    os.makedirs(BIN_DIR, exist_ok=True)

    if platform.system() == "Windows":
        if flags.get("leo_cmd_created"):
            print("✅ 'leo' command already exists. Skipping...")
            return
        with open(LEO_SCRIPT_WIN, "w") as f:
            f.write(f"@echo off\n\"{VENV_PYTHON}\" \"{os.path.join(os.getcwd(), 'leo.py')}\" %*\n")
        flags["leo_cmd_created"] = True
        save_flags(flags)
        print("✅ Created 'leo' command for Windows.")

    else:
        if flags.get("leo_script_created"):
            print("✅ 'leo' command already exists. Skipping...")
            return
        with open(LEO_SCRIPT_LINUX, "w") as f:
            f.write(f"#!/bin/bash\n\"{VENV_PYTHON}\" \"{os.path.join(os.getcwd(), 'leo.py')}\" \"$@\"\n")
        os.chmod(LEO_SCRIPT_LINUX, 0o755)
        flags["leo_script_created"] = True
        save_flags(flags)
        print("✅ Created 'leo' command for Linux/macOS.")


def add_to_path():
    """Add ~/.leo_cli/bin (or Windows equivalent) to PATH."""
    flags = load_flags()
    if flags.get("path_added"):
        print("✅ PATH already updated. Skipping...")
        return

    if platform.system() == "Windows":
        PATH_CMD = f'setx PATH "%PATH%;{BIN_DIR}"'
        run_command(PATH_CMD, hide_output=False)
        flags["path_added"] = True
        save_flags(flags)
        print(f"✅ Added '{BIN_DIR}' to system PATH. Restart your terminal to use 'leo'.")

    else:
        BASHRC = os.path.expanduser("~/.bashrc")
        ZSHRC = os.path.expanduser("~/.zshrc")
        export_cmd = f'export PATH="{BIN_DIR}:$PATH"'

        for shell_rc in [BASHRC, ZSHRC]:
            if os.path.exists(shell_rc):
                with open(shell_rc, "a") as f:
                    f.write(f"\n# Add LEO CLI to PATH\n{export_cmd}\n")

        flags["path_added"] = True
        save_flags(flags)
        print(f"✅ Added '{BIN_DIR}' to system PATH. Restart your terminal or run 'source ~/.bashrc'.")


def setup_file_associations():
    """Ensure Windows executes 'leo' as a command."""
    flags = load_flags()
    if platform.system() != "Windows" or flags.get("file_associations_set"):
        return

    if is_admin():
        print("🔹 Ensuring Windows executes 'leo' as a command...")
        subprocess.run(["cmd.exe", "/c", "assoc .leo=Python.File"], check=True)
        subprocess.run(["cmd.exe", "/c", f"ftype Python.File={VENV_PYTHON} %1 %*"], check=True)
        flags["file_associations_set"] = True
        save_flags(flags)
        print("✅ 'leo' is now recognized as a Python script.")
    else:
        print("⚠️ Skipped file association changes (requires Administrator privileges).")
        print("ℹ️ To manually set file associations, run:")
        print('   cmd.exe /c "assoc .leo=Python.File"')
        print(f'   cmd.exe /c "ftype Python.File={VENV_PYTHON} %1 %*"')


def run_as_admin():
    """Re-run the script as administrator if needed (Windows only)."""
    if platform.system() == "Windows" and not is_admin():
        print("⚠️ Some setup steps require administrator privileges.")
        print("🔹 Re-run the script as administrator to complete setup:")
        print(f"   powershell Start-Process python -ArgumentList \"install.py\" -Verb RunAs")


if __name__ == "__main__":
    print("🚀 Setting up LEO CLI...")

    create_virtualenv()
    create_executable()
    add_to_path()
    setup_file_associations()
    run_as_admin()  # Show message if admin privileges are needed

    print("🎉 LEO CLI is ready! Try running:")
    print("   leo --help")
