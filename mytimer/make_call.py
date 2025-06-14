"""
LiveKit call dispatch module for the Azure Function timer trigger.

This module provides functionality to dispatch outbound calls using LiveKit's
SIP integration. It handles the creation of agent dispatches and SIP participants
for outbound calling.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# from dotenv import load_dotenv
from livekit import api

# Load environment variables for local development
# In Azure, these should be set as Application Settings
# load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

# Set up logging
logger = logging.getLogger("mytimer-call-dispatch")
logger.setLevel(logging.INFO)

# Define required environment variables
REQUIRED_ENV_VARS = [
    "LIVEKIT_URL",
    "LIVEKIT_API_KEY",
    "LIVEKIT_API_SECRET",
    "PHONE_NUMBER",
    "TRANSFER_TO",
    "ROOM_NAME",
    "AGENT_NAME",
    "SIP_OUTBOUND_TRUNK_ID",
]

def validate_environment() -> Tuple[bool, List[str]]:
    """
    Validate that all required environment variables are set and have valid values.
    
    Returns:
        Tuple[bool, List[str]]: A tuple containing a boolean indicating success
        and a list of error messages if any validations fail.
    """
    # Check for missing required variables
    missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing_vars:
        return (False, [f"Missing required environment variables: {', '.join(missing_vars)}"])
    
    # Validate SIP trunk ID format if present
    trunk_id = os.getenv("SIP_OUTBOUND_TRUNK_ID")
    if trunk_id and not trunk_id.startswith("ST_"):
        return (False, [f"Invalid SIP_OUTBOUND_TRUNK_ID '{trunk_id}'. It must start with 'ST_'."])
    
    return (True, [])

def log_and_exit(message: str, exit_code: int = 1) -> None:
    """
    Log an error message and exit with the specified status code.
    
    Args:
        message: The error message to log.
        exit_code: The exit code to use (default: 1).
    """
    logger.error(message)
    sys.exit(exit_code)

async def make_call() -> None:
    """
    Creates a LiveKit agent dispatch and a SIP participant to call a predefined phone number.
    
    This function performs the following steps:
    1. Validates all required environment variables are set
    2. Validates the SIP trunk ID format
    3. Creates a LiveKit API client
    4. Creates an agent dispatch with call metadata
    5. Creates a SIP participant to initiate the outbound call
    
    Raises:
        SystemExit: If required environment variables are missing or invalid.
        Exception: If there's an error during LiveKit API operations.
    """
    # Validate environment variables before proceeding
    is_valid, missing_vars = validate_environment()
    if not is_valid:
        log_and_exit(
            f"Missing required environment variables: {', '.join(missing_vars)}. "
            "Please check your configuration."
        )
    
    # Fetch configuration from environment variables
    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_api_key = os.getenv("LIVEKIT_API_KEY")
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
    phone_number = os.getenv("PHONE_NUMBER")
    transfer_to = os.getenv("TRANSFER_TO")
    room_name = os.getenv("ROOM_NAME")
    agent_name = os.getenv("AGENT_NAME")
    outbound_trunk_id = os.getenv("SIP_OUTBOUND_TRUNK_ID")

    # Validate SIP trunk ID format
    if not outbound_trunk_id.startswith("ST_"):
        log_and_exit(
            f"Invalid SIP_OUTBOUND_TRUNK_ID '{outbound_trunk_id}'. "
            "It must start with 'ST_'. Please check your configuration."
        )

    # Initialize LiveKit API client
    lkapi = None
    try:
        lkapi = api.LiveKitAPI(livekit_url, livekit_api_key, livekit_api_secret)
        
        # Create call metadata
        metadata = {
            "phone_number": phone_number,
            "transfer_to": transfer_to
        }
        
        # Create agent dispatch
        logger.info("Creating dispatch for agent '%s' in room '%s'", agent_name, room_name)
        dispatch = await lkapi.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                agent_name=agent_name,
                room=room_name,
                metadata=json.dumps(metadata)
            )
        )
        logger.info("Successfully created dispatch: %s", dispatch.id)
        
        # Create SIP participant for outbound call
        logger.info(
            "Dialing %s to room '%s' via trunk '%s'",
            phone_number, room_name, outbound_trunk_id
        )
        sip_participant = await lkapi.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                room_name=room_name,
                sip_trunk_id=outbound_trunk_id,
                sip_call_to=phone_number,
                participant_identity=f"phone_user_{room_name}",
            )
        )
        logger.debug("SIP participant object: %r", sip_participant)
        logger.debug("SIP participant type: %s", type(sip_participant))
        logger.info(
            "Successfully created SIP participant: %s",
            sip_participant.participant_identity
        )
        
    except Exception as e:
        logger.error(
            "An error occurred during LiveKit operation: %s", str(e),
            exc_info=True
        )
        raise  # Re-raise to allow the caller to handle the exception
        
    finally:
        # Ensure proper cleanup of resources
        if lkapi:
            await lkapi.aclose()