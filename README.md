# Azure Function Timer: Deployment & TDD

## Overview
This project implements an Azure Functions timer-triggered Python function that logs a message every 30 minutes. The project follows strict Test-Driven Development (TDD) and is production-ready, with automated deployment workflows using Azure CLI and Taskfile.

---

## Project Structure
- `mytimer/` : Azure Function timer code and configuration
  - `__init__.py` : Timer function implementation (logs timestamped message)
  - `function.json` : Timer trigger binding (every 30 minutes)
- `tests/` : Pytest unit tests for the timer function
- `requirements.txt` : Python dependencies (`azure-functions`, `pytest`)
- `Taskfile.yaml` : Automated deployment and management tasks
- `tasks/prd-azure-function-timer.md` : Product requirements and implementation plan

---

## Prerequisites
- Python 3.11+
- Azure CLI (latest)
- Access to an Azure subscription with permissions to create resources

---

## Local Development & Testing
1. **Set up a virtual environment:**
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Run tests with pytest:**
   ```sh
   pytest
   ```

---

## Deployment Workflow
All deployment steps are automated via `Taskfile.yaml` and the `task` CLI.

### 1. Azure Login & Setup
```sh
task login
task set-subscription
```

### 2. Create Azure Resources (one-time)
```sh
task create-storage-account
task create-function-app
```

### 3. Deploy Function Code
```sh
task zip-deploy
```

### 4. Check Deployment Logs
```sh
task logs
```

---

## Runtime Log Validation
- **Application Insights**: For runtime execution logs, use the Azure Portal:
  1. Go to your Function App.
  2. Open the Application Insights blade.
  3. Query logs for messages like `[mytimer] Timer triggered at ...`.
- **Note**: Real-time log streaming is not supported via CLI for Linux Function Apps.

---

## TDD & Testing
- All code changes are test-driven (`pytest` in `tests/`).
- The timer function only logs a message; no external API calls or emails.

---

## Cleanup
- `.venv/` and build artifacts are excluded via `.gitignore`.
- To remove Azure resources, use the Azure Portal or CLI as appropriate.

---

## References
- [Azure Functions Python Developer Guide](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [Azure CLI Documentation](https://learn.microsoft.com/en-us/cli/azure/)
