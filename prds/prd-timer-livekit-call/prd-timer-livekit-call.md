# Timer-Triggered LiveKit Call Dispatch

## 1. Introduction/Overview

This feature expands the Azure Function timer so that, when triggered, it automatically dispatches an outbound LiveKit call to a specified phone number. The primary use cases are for automated outbound calls and calendar event reminders to end customers. The goal is to ensure that users receive timely reminders via phone calls, triggered by a scheduled timer event.

## 2. Goals

- Automatically dispatch a LiveKit call to a predefined phone number whenever the timer triggers.
- Log all call dispatch attempts and errors for monitoring and troubleshooting.
- Ensure the process is asynchronous and non-blocking.

## 3. User Stories

- As a user, I want the system to call a number when the timer triggers, so that the user will be reminded of their calendar event.

## 4. Functional Requirements

1. The system must trigger on a schedule (via Azure Function timer).
2. When triggered, the function must dispatch a LiveKit call to a predefined phone number.
3. The call must use the following environment variables for configuration:
    - `LIVEKIT_URL`
    - `LIVEKIT_API_KEY`
    - `LIVEKIT_API_SECRET`
    - `SIP_OUTBOUND_TRUNK_ID`
    - `AGENT_NAME`
    - `ROOM_NAME`
    - `PHONE_NUMBER`
    - `TRANSFER_TO`
4. The process must be asynchronous and non-blocking (the timer should not wait for the call to complete).
5. All successful call dispatches must be logged.
6. All errors or exceptions must be logged with sufficient detail for troubleshooting.
7. The system must not send SMS or retry failed calls.
8. The function must fail gracefully if required environment variables are missing or invalid.

## 5. Non-Goals (Out of Scope)

- Sending SMS messages.
- Retrying failed calls.
- Handling dynamic lists of phone numbers or targets.
- Providing a user interface or reporting dashboard.

## 6. Design Considerations

- Backend-only automation; no UI is required.
- Logging should be clear and accessible via Azure monitoring tools.
- Use the existing `make_call.py` logic for LiveKit call dispatch.

## 7. Technical Considerations

- The function must use the environment variables as described for configuration.
- The LiveKit call dispatch logic should be invoked asynchronously (e.g., using `asyncio.create_task` or similar).
- The function should use the existing `make_call.py` as a module or callable.
- Ensure compatibility with Azure Functions’ Python runtime and logging.

## 8. Success Metrics

- Number of successful calls dispatched (tracked via logs).
- Error rate (number of failed dispatch attempts vs. total attempts).
- No unhandled exceptions or timer failures in production.

## 9. Open Questions

- None at this time.

---

**Location:**  
This document is saved as `prds/prd-timer-livekit-call/prd-timer-livekit-call.md`.
