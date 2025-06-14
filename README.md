# LiveKit Outbound Call Scheduler

## Overview
This project implements an Azure Functions timer-triggered Python function that initiates outbound calls using LiveKit's SIP integration. The function creates an agent dispatch and a SIP participant to place outbound calls on a schedule. The project follows strict Test-Driven Development (TDD) and is production-ready, with automated deployment workflows using Azure CLI and Taskfile.

---

## Project Structure
- `mytimer/` : Azure Function timer code and configuration
  - `__init__.py` : Timer function implementation with async call dispatch
  - `make_call.py` : LiveKit call dispatch logic
  - `function.json` : Timer trigger binding (every 30 minutes)
- `tests/` : Pytest unit tests for the function
  - `test_mytimer.py` : Unit tests for the timer and call dispatch logic
- `requirements.txt` : Python dependencies (`azure-functions`, `pytest`, `livekit-api`, `python-dotenv`)
- `Taskfile.yaml` : Automated deployment and management tasks
- `prds/` : Product requirements and implementation plans
  - `prd-timer-livekit-call/` : Requirements for the LiveKit call scheduler
    - `tasks/` : Task breakdown and implementation tracking

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

## Taskfile.yaml Tasks

The following tasks are available via the Taskfile.yaml and the `task` CLI:

- `azurite:local`: Run Azurite (Azure Storage Emulator) locally via Docker for local development.
- `venv:create`: Create a new Python virtual environment.
- `venv:activate`: Activate the virtual environment.
- `install-deps`: Install Python dependencies from requirements.txt.
- `clean-venv`: Remove the virtual environment.
- `login`: Log in to Azure CLI.
- `set-subscription`: Set the active Azure subscription for deployments.
- `create-storage-account`: Create the required Azure Storage Account.
- `create-function-app`: Create a new Azure Function App (Python 3.11, Linux, Consumption plan).
- `package`: Create a deployment package with all dependencies.
- `zip-deploy`: Deploy the function code to Azure using zip deploy.
- `logs`: Show deployment logs for the Azure Function App.
- `get-function-key`: Get the function key for the mytimer function.
- `get-master-key`: Get the master key for the function app.
- `trigger-function`: Manually trigger the mytimer function using the admin endpoint.
- `set-env-vars`: Set all required environment variables for the Azure Function App.
- `list-settings`: List current environment variables for the Azure Function App.

Run `task --list` to see all available tasks and their descriptions.

---

## Environment Variables

The following environment variables must be configured in your Azure Function App settings:

### LiveKit Configuration
- `LIVEKIT_URL`: The URL of your LiveKit instance (e.g., `wss://your-instance.livekit.io`)
- `LIVEKIT_API_KEY`: API key with permissions to create dispatches and SIP participants
- `LIVEKIT_API_SECRET`: Corresponding API secret for the key above

### Call Configuration
- `PHONE_NUMBER`: The phone number to call (e.g., `+15551234567`)
- `TRANSFER_TO`: The SIP URI or number to transfer to after call is answered
- `ROOM_NAME`: The LiveKit room name to use for the call
- `AGENT_NAME`: Name of the agent to use for the dispatch
- `SIP_OUTBOUND_TRUNK_ID`: The SIP trunk ID (must start with 'ST_')

## Logging

Log messages follow this format:
- `[mytimer-call-dispatch] <message>` for call dispatch related logs
- `[mytimer] <message>` for timer function logs

## Runtime Log Validation
- **Application Insights**: For runtime execution logs, use the Azure Portal:
  1. Go to your Function App
  2. Open the Application Insights blade
  3. Query logs for messages like `[mytimer-call-dispatch]` or `[mytimer]`
- **Note**: Real-time log streaming is not supported via CLI for Linux Function Apps.

---

## TDD & Testing
- All code changes are test-driven (`pytest` in `tests/`).
- Tests mock the LiveKit API to avoid making real calls during testing.
- Run tests with: `pytest -v`

## Error Handling
- Missing or invalid environment variables will cause the function to log an error and exit.
- LiveKit API errors are caught, logged, and re-raised for visibility in Application Insights.

---

## Cleanup
- `.venv/` and build artifacts are excluded via `.gitignore`.
- To remove Azure resources, use the Azure Portal or CLI as appropriate.

---

## References
- [Azure Functions Python Developer Guide](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python)
- [Azure CLI Documentation](https://learn.microsoft.com/en-us/cli/azure/)
