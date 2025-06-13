import asyncio
import os
import logging
import json
from pathlib import Path
from dotenv import load_dotenv
from livekit import api

# Load environment variables for local development
# In Azure, these should be set as Application Settings
load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

# Set up logging
logger = logging.getLogger("mytimer-call-dispatch")
logger.setLevel(logging.INFO)

async def make_call():
    """
    Creates a LiveKit agent dispatch and a SIP participant to call a predefined phone number.
    All configuration is read from environment variables.
    """
    # Fetch configuration from environment variables
    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_api_key = os.getenv("LIVEKIT_API_KEY")
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
    phone_number = os.getenv("PHONE_NUMBER")
    transfer_to = os.getenv("TRANSFER_TO")
    room_name = os.getenv("ROOM_NAME")
    agent_name = os.getenv("AGENT_NAME")
    outbound_trunk_id = os.getenv("SIP_OUTBOUND_TRUNK_ID")

    # Validate required environment variables
    required_vars = {
        "LIVEKIT_URL": livekit_url,
        "LIVEKIT_API_KEY": livekit_api_key,
        "LIVEKIT_API_SECRET": livekit_api_secret,
        "PHONE_NUMBER": phone_number,
        "TRANSFER_TO": transfer_to,
        "ROOM_NAME": room_name,
        "AGENT_NAME": agent_name,
        "SIP_OUTBOUND_TRUNK_ID": outbound_trunk_id,
    }

    missing_vars = [key for key, value in required_vars.items() if not value]
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return

    if not outbound_trunk_id.startswith("ST_"):
        logger.error(f"SIP_OUTBOUND_TRUNK_ID '{outbound_trunk_id}' is invalid. It must start with 'ST_'.")
        return

    lkapi = api.LiveKitAPI(livekit_url, livekit_api_key, livekit_api_secret)
    
    try:
        logger.info(f"Creating dispatch for agent '{agent_name}' in room '{room_name}'")
        metadata = {
            "phone_number": phone_number,
            "transfer_to": transfer_to
        }
        dispatch = await lkapi.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                agent_name=agent_name, room=room_name, metadata=json.dumps(metadata)
            )
        )
        logger.info(f"Successfully created dispatch: {dispatch.id}")
        
        logger.info(f"Dialing {phone_number} to room '{room_name}' via trunk '{outbound_trunk_id}'")
        sip_participant = await lkapi.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                room_name=room_name,
                sip_trunk_id=outbound_trunk_id,
                sip_call_to=phone_number,
                participant_identity="phone_user",
            )
        )
        logger.info(f"Successfully created SIP participant: {sip_participant.participant.identity}")
    except Exception as e:
        logger.error(f"An error occurred during LiveKit operation: {e}", exc_info=True)
    finally:
        await lkapi.aclose()