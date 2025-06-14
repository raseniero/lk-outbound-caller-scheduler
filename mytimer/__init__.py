"""Azure Function for scheduling and dispatching outbound calls using LiveKit SIP integration.

This module provides a timer-triggered Azure Function that initiates outbound calls
according to a predefined schedule. It handles the async nature of the LiveKit API calls
and includes proper error handling and logging.
"""
from __future__ import annotations

import asyncio
import datetime
import logging
from typing import Optional, cast

import azure.functions as func

from .make_call import make_call

# Create a singleton event loop that will be reused across function invocations
_loop: Optional[asyncio.AbstractEventLoop] = None

def get_event_loop() -> asyncio.AbstractEventLoop:
    """Get or create the event loop for this function app.
    
    Returns:
        asyncio.AbstractEventLoop: The event loop instance.
        
    Note:
        This function maintains a singleton event loop to avoid creating
        multiple loops which can lead to resource leaks.
    """
    global _loop
    if _loop is None or _loop.is_closed():
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)
    return _loop

async def _run_async(max_retries: int = 3, retry_delay: float = 1.0) -> None:
    """Helper function to run the async make_call with retry logic and proper error handling.
    
    Args:
        max_retries: Maximum number of retry attempts for failed calls.
        retry_delay: Initial delay between retries in seconds (will be doubled after each retry).
        
    Raises:
        Exception: If all retry attempts are exhausted and the call still fails.
        
    Note:
        This implements an exponential backoff retry mechanism for transient failures.
    """
    last_exception: Optional[Exception] = None
    
    for attempt in range(max_retries + 1):
        try:
            logging.info("Dispatching outbound call (attempt %d/%d)", 
                        attempt + 1, max_retries + 1)
            await make_call()
            logging.info("Call dispatch completed successfully")
            return
            
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                logging.warning(
                    "Call attempt %d failed (will retry in %.1fs): %s",
                    attempt + 1, wait_time, str(e),
                    exc_info=attempt == 0  # Full traceback only on first attempt
                )
                await asyncio.sleep(wait_time)
            else:
                logging.error(
                    "All %d call attempts failed. Last error: %s",
                    max_retries + 1, str(e),
                    exc_info=True
                )
    
    # If we get here, all retries failed
    if last_exception is not None:
        raise last_exception

def main(mytimer: func.TimerRequest) -> None:
    """Azure Function that runs on a timer to dispatch outbound calls.
    
    This is the main entry point for the Azure Function. It handles the timer trigger,
    manages the event loop, and ensures proper cleanup of resources.
    
    Args:
        mytimer: The timer trigger that caused this function to run.
        
    Raises:
        RuntimeError: If there's an error initializing or running the event loop.
        Exception: If there's an unhandled exception in the async call logic.
    """
    if not isinstance(mytimer, func.TimerRequest):
        raise ValueError("Invalid timer request object")
    
    utc_timestamp = datetime.datetime.now(datetime.UTC).isoformat()
    logging.info('Python timer trigger function started at %s', utc_timestamp)

    if mytimer.past_due:
        logging.warning('The timer is past due!')
    
    # Get the event loop
    loop = get_event_loop()
    
    try:
        # If the loop is already running, schedule the task to run in the background
        if loop.is_running():
            logging.debug("Event loop is already running, scheduling background task")
            future = asyncio.ensure_future(_run_async())
            # Add error callback to log any unhandled exceptions
            def handle_task_result(task: asyncio.Task[None]) -> None:
                try:
                    task.result()
                except Exception as e:
                    logging.error("Background task failed: %s", str(e), exc_info=True)
            future.add_done_callback(handle_task_result)
        else:
            # Otherwise, run the loop until the task is complete
            logging.debug("Starting new event loop for call dispatch")
            loop.run_until_complete(_run_async())
            
    except Exception as e:
        logging.critical("Unhandled exception in timer function: %s", str(e), exc_info=True)
        raise
    finally:
        # Clean up any resources if needed
        logging.debug("Timer function execution completed")