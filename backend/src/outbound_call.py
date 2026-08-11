"""
Day 6 — Outbound Call Script for DukaanSaathi (दुकानसाथी)
Track: Local Commerce
Use Case: Order Confirmation / Restock Nudge

This script places an outbound SIP call via LiveKit Cloud to a Linphone user,
delivering a restock nudge or order follow-up from Sharma General Store.
"""

import asyncio
import os
import logging
import uuid

from dotenv import load_dotenv
from livekit import api
from livekit.protocol.sip import CreateSIPParticipantRequest

load_dotenv(".env.local")

logger = logging.getLogger("outbound_call")
logging.basicConfig(level=logging.INFO)

# ── Configuration ──────────────────────────────────────────────────────────────
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
SIP_TRUNK_ID = os.getenv("LIVEXIT_SIP_TRUNK_ID")  # Matches .env.local key name
SIP_CALL_TO = os.getenv("LINEPHONE_SIP_URI")  # e.g. sip:username@sip.linphone.org


async def make_outbound_call(
    sip_uri: str | None = None,
    customer_name: str = "Customer",
    call_reason: str = "restock_nudge",
):
    """
    Place an outbound SIP call to a customer via LiveKit Cloud.

    Args:
        sip_uri: The SIP URI to call (e.g. sip:user@sip.linphone.org).
        customer_name: Name of the customer being called.
        call_reason: Why we are calling — 'restock_nudge' or 'order_confirmation'.
    """
    target_uri = sip_uri or SIP_CALL_TO

    if not all([LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET]):
        raise ValueError("Missing LIVEKIT_URL, LIVEKIT_API_KEY, or LIVEKIT_API_SECRET in .env.local")

    if not SIP_TRUNK_ID:
        raise ValueError("Missing LIVEXIT_SIP_TRUNK_ID in .env.local")

    if not target_uri:
        raise ValueError("No SIP URI provided. Set LINEPHONE_SIP_URI in .env.local or pass sip_uri argument.")

    # LiveKit expects a phone number or SIP user ID for sip_call_to (e.g. "aimlgyanesh" or "+1234567890"), not a full URI
    sip_number = target_uri
    if sip_number.startswith("sip:"):
        sip_number = sip_number[4:]
    if "@" in sip_number:
        sip_number = sip_number.split("@")[0]

    # Create a unique room for this outbound call
    room_name = f"outbound_call_{uuid.uuid4().hex[:8]}"

    logger.info(f"🔔 Placing outbound call...")
    logger.info(f"   Target SIP User : {sip_number} (from {target_uri})")
    logger.info(f"   Customer Name   : {customer_name}")
    logger.info(f"   Call Reason     : {call_reason}")
    logger.info(f"   Room Name       : {room_name}")
    logger.info(f"   SIP Trunk ID    : {SIP_TRUNK_ID}")

    # Build participant attributes so the agent knows this is an outbound call
    participant_attributes = {
        "call_direction": "outbound",
        "call_reason": call_reason,
        "customer_name": customer_name,
    }

    lk_api = api.LiveKitAPI(
        url=LIVEKIT_URL,
        api_key=LIVEKIT_API_KEY,
        api_secret=LIVEKIT_API_SECRET,
    )

    try:
        # Create the SIP participant (this dials out)
        sip_participant = await lk_api.sip.create_sip_participant(
            CreateSIPParticipantRequest(
                sip_trunk_id=SIP_TRUNK_ID,
                sip_call_to=sip_number,
                room_name=room_name,
                participant_identity=f"sip_customer_{uuid.uuid4().hex[:6]}",
                participant_name=customer_name,
                participant_attributes=participant_attributes,
                play_dialtone=True,
            )
        )

        logger.info(f"✅ Outbound call placed successfully!")
        logger.info(f"   SIP Participant ID: {sip_participant.participant_id}")
        logger.info(f"   Room: {room_name}")

        # Explicitly dispatch agent worker to the room
        import json
        try:
            dispatch = await lk_api.agent_dispatch.create_dispatch(
                api.CreateAgentDispatchRequest(
                    agent_name="my-agent",
                    room=room_name,
                    metadata=json.dumps({
                        "call_direction": "outbound",
                        "call_reason": call_reason,
                        "customer_name": customer_name,
                    }),
                )
            )
            logger.info(f"🤖 Agent dispatched successfully to room (Dispatch ID: {dispatch.id})")
        except Exception as dispatch_err:
            logger.warning(f"⚠️ Agent dispatch warning: {dispatch_err}")

        logger.info(f"")
        logger.info(f"📞 Phone is ringing on Linphone... Answer the call!")
        logger.info(f"   The DukaanSaathi agent will join automatically and deliver the message.")

    except Exception as e:
        logger.error(f"❌ Failed to place outbound call: {e}")
        raise
    finally:
        await lk_api.aclose()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="DukaanSaathi Outbound Call — Sharma General Store")
    parser.add_argument(
        "--sip-uri",
        type=str,
        default=None,
        help="SIP URI to call (defaults to LINEPHONE_SIP_URI from .env.local)",
    )
    parser.add_argument(
        "--customer-name",
        type=str,
        default="Customer",
        help="Name of the customer being called (for personalized greeting)",
    )
    parser.add_argument(
        "--reason",
        type=str,
        choices=["restock_nudge", "order_confirmation"],
        default="restock_nudge",
        help="Reason for the outbound call",
    )
    args = parser.parse_args()

    asyncio.run(
        make_outbound_call(
            sip_uri=args.sip_uri,
            customer_name=args.customer_name,
            call_reason=args.reason,
        )
    )
