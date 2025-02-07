# 🦁 LEO Client - Command Line Interface (CLI)

## 📜 Overview

The LEO Client is a **powerful AI-powered command-line assistant** that enables users to generate and execute system commands using natural language prompts. It acts as an interface between the user and the **LEO API**, processing input, handling execution modes, and securely managing secrets.

This CLI tool supports:  
✅ **AI-Powered Command Generation** (via Vertex AI)  
✅ **Context-Aware Execution** (interactive questioning for missing details)  
✅ **Secure Secrets Management** (Google Secret Manager integration)  
✅ **Autonomous & User-Controlled Modes**  
✅ **Logging & Feedback System** (local & cloud logging)  

---

## 📂 Directory Structure

```
client/
│── leo.py             # Main CLI entry point
│── config.py          # Stores API endpoint & settings
│── prompts.py         # Handles interactive questioning
│── executor.py        # Manages command execution (manual & autonomous)
│── logger.py          # Logs local CLI execution history
│── secrets.py         # Retrieves secrets from Google Secret Manager
│── requirements.txt   # Dependencies for CLI
│── README.md          # Documentation for the client module
```

---

## 📜 Detailed File Descriptions

### **1️⃣ leo.py - CLI Entry Point**
This is the **main script** that serves as the **command-line interface** for LEO. It handles user input, sends requests to the **LEO API**, and processes responses.

🔹 **Responsibilities:**  
- Parses **natural language prompts** from the user.  
- Calls the **LEO API** to generate commands.  
- Displays execution results and logs output.  
- Handles **interactive questioning** when missing details are detected.  

🔹 **Example Usage:**  
```bash
python leo.py "Deploy a new Kubernetes pod"
```

---

### **2️⃣ config.py - Configuration Settings**
Stores **API URLs, execution modes, and environment settings**. This file allows easy customization of CLI behavior.

🔹 **Responsibilities:**  
- Defines **API endpoints** for communicating with the LEO backend.  
- Stores **execution settings** (e.g., auto/manual mode).  
- Reads **environment variables** (if needed).  

🔹 **Example Config Structure:**  
```python
API_URL = "https://leo-api.example.com"
EXECUTION_MODE = "manual"  # Options: "manual" | "auto"
```

---

### **3️⃣ prompts.py - Interactive Questioning Module**
Handles **interactive questioning** when missing details are detected in a prompt. This improves command accuracy.

🔹 **Responsibilities:**  
- **Identifies missing context** from the user query.  
- Generates **clarifying questions** dynamically.  
- Processes user responses and **refines command execution**.  

🔹 **Example Workflow:**  
```python
from prompts import ask_for_details

missing_info = ["container name", "namespace"]
user_input = ask_for_details(missing_info)
```

---

### **4️⃣ executor.py - Command Execution Manager**
Handles **command execution** in both **manual and autonomous modes**. It ensures commands are run **safely and efficiently**.

🔹 **Responsibilities:**  
- Runs system commands locally or forwards them to the LEO API.  
- Supports **manual approval mode** for user verification.  
- Handles **error detection and retries**.  

🔹 **Example Execution Flow:**  
```python
from executor import execute_command

command = "kubectl get pods"
execute_command(command, mode="manual")
```

---

### **5️⃣ logger.py - Execution Logging System**
Manages **logging of executed commands** and their outputs for debugging and analysis.

🔹 **Responsibilities:**  
- Logs **command execution history**.  
- Supports **local file logging** and **Google Cloud Logging** integration.  
- Tracks **error messages and retries**.  

🔹 **Example Log Entry:**  
```json
{
  "timestamp": "2025-02-04T12:34:56Z",
  "command": "kubectl get pods",
  "status": "success",
  "output": "3 pods running"
}
```

---

### **6️⃣ secrets.py - Secure Secrets Management**
Handles **retrieving API keys and sensitive credentials** from **Google Secret Manager**, ensuring security.

🔹 **Responsibilities:**  
- Fetches **secure credentials** without storing them locally.  
- Injects **secrets into command execution** securely.  

🔹 **Example Usage:**  
```python
from secrets import get_secret

api_key = get_secret("LEO_API_KEY")
```

---

## 🚀 Getting Started

### **📥 Installation**

```bash
pip install -r requirements.txt
```

### **⚡ Usage Example**

```bash
python leo.py "Deploy a new PostgreSQL database"
```

### **🌍 Running in Different Execution Modes**
- **Manual Mode:** Prompts the user before executing commands.  
- **Autonomous Mode:** Runs commands automatically.  

Modify `config.py`:
```python
EXECUTION_MODE = "auto"  # Change to "manual" for user approval
```

---

## 🔧 **Configuration Options**
Modify `config.py` to adjust behavior:

| Option            | Description |
|------------------|-------------|
| `API_URL`        | URL of the LEO API backend |
| `EXECUTION_MODE` | `"manual"` (asks user for approval) or `"auto"` (executes automatically) |
| `LOGGING`        | Enable/disable local logging |
| `SECRETS_MODE`   | `"local"` (for development) or `"cloud"` (uses Google Secret Manager) |

---

## 🛡️ **Security Considerations**
- **Secrets are never stored in plaintext**; use Google Secret Manager.  
- **Execution is sandboxed** to prevent malicious commands.  
- **User approval is required in manual mode** for safety.  

---

## 📌 Contributing
Contributions are welcome! Submit a pull request or open an issue to improve the LEO CLI.

## 📜 License
This project is licensed under the **MIT License**.

---

🚀 **Now you're ready to use LEO Client for AI-powered command execution!** 🚀
