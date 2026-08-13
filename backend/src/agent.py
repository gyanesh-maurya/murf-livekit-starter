import asyncio
import logging

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentSession,
    AgentServer,
    JobContext,
    JobProcess,
    cli,
    tokenize,
    room_io,
    function_tool,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.agents.llm import ChatMessage

# Import the Day 2 Local Commerce system prompt
from prompt import SYSTEM_PROMPT, SILENCE_REPROMPT, SILENCE_GOODBYE
from db import (
    init_db,
    lookup_customer,
    save_customer,
    delete_customer,
    create_escalation_ticket,
    record_call_start,
    record_call_end,
    get_analytics_summary,
)
from catalog import search_product, calculate_order_total

logger = logging.getLogger("agent")

load_dotenv(".env.local")


class Assistant(Agent):
    def __init__(self, user_id: str, custom_instructions: str = "", tools_used_list: list = None) -> None:
        full_instructions = f"{SYSTEM_PROMPT}\n\n# CURRENT CALL CONTEXT\n{custom_instructions}" if custom_instructions else SYSTEM_PROMPT
        super().__init__(instructions=full_instructions)
        self._user_id = user_id
        self._tools_used = tools_used_list if tools_used_list is not None else []

    @function_tool
    async def lookup_customer(self, user_id: str) -> str:
        """
        Look up a customer by their user_id to check if they have called before.
        Call this at the START of every conversation to check if the caller is known.
        Returns the customer's saved data as JSON, or "not_found" if they are new.
        """
        result = lookup_customer(user_id)
        if result is None:
            import json
            return json.dumps({"status": "not_found", "user_id": user_id})
        import json
        return json.dumps({"status": "found", "data": result}, ensure_ascii=False)

    @function_tool
    async def save_customer(
        self,
        name: str,
        language_preference: str,
        facts: str,
        user_id: str = "",
    ) -> str:
        """
        Save or update a customer's information after getting their explicit consent.
        NEVER call this without asking the customer first.

        Args:
            name: The customer's name (e.g. "Ramesh", "Pooja").
            language_preference: The language they prefer (e.g. "hindi", "english", "hinglish").
            facts: A JSON string or text of key-value facts like past_inquiries, usual_quantities, area.
        """
        self._tools_used.append("save_customer")
        import json
        actual_user_id = self._user_id or user_id or "demo_customer_1"
        try:
            facts_dict = json.loads(facts) if isinstance(facts, str) else facts
        except json.JSONDecodeError:
            facts_dict = {"note": facts}

        result = save_customer(
            user_id=actual_user_id,
            name=name,
            language_preference=language_preference,
            facts=facts_dict,
        )
        logger.info(f"Successfully saved customer data to DB for user_id={actual_user_id}, name={name}")
        return json.dumps(
            {"status": "saved", "user_id": actual_user_id, "data": result}, ensure_ascii=False
        )

    @function_tool
    async def delete_customer(self, user_id: str = "") -> str:
        """
        Delete a customer's data when they ask to be forgotten.
        Call this when a user says 'mera data delete karo', 'mujhe bhool jao', or 'forget me'.
        """
        self._tools_used.append("delete_customer")
        actual_user_id = self._user_id or user_id or "demo_customer_1"
        deleted = delete_customer(actual_user_id)
        import json
        if deleted:
            return json.dumps({"status": "deleted", "user_id": actual_user_id})
        return json.dumps({"status": "not_found", "user_id": actual_user_id})

    @function_tool
    async def lookup_product(self, product_name: str) -> str:
        """
        Look up real-time stock availability, unit price, and rate timestamp for a specific product or item in Sharma General Store.
        Call this whenever a customer asks about a product's price, availability, or stock (e.g. 'Atta ka price kya hai', 'Oil stock mein hai kya').

        Args:
            product_name: The name or keyword of the product to search (e.g. "atta", "mustard oil", "maggi", "cheeni", "milk").
        """
        self._tools_used.append("lookup_product")
        import json
        result = search_product(product_name)
        return json.dumps(result, ensure_ascii=False)

    @function_tool
    async def calculate_bill(self, items_json: str) -> str:
        """
        Calculate total cost, subtotal, delivery eligibility (free delivery above ₹500, else ₹30), and estimated delivery time for a list of items.
        Call this when a customer asks how much their order will cost, or asks for a total bill for multiple items.

        Args:
            items_json: A JSON string list of objects with 'name' and 'quantity' (e.g. '[{"name": "atta", "quantity": 1}, {"name": "sugar", "quantity": 2}]').
        """
        self._tools_used.append("calculate_bill")
        import json
        result = calculate_order_total(items_json)
        return json.dumps(result, ensure_ascii=False)

    @function_tool
    async def create_escalation(
        self,
        customer_name: str,
        category: str,
        summary: str,
        urgency: str = "medium",
    ) -> str:
        """
        Create a human help request/ticket for the store owner (Ramesh Sharma).

        CRITICAL PRE-CONDITION: DO NOT CALL THIS TOOL IN THE SAME TURN AS ASKING PERMISSION!
        1. When a user reports a problem/dispute, FIRST ask them for permission: "क्या मैं रमेश भाई को आपकी यह रिक्वेस्ट भेज दूँ?"
        2. DO NOT call this tool yet! Wait for the user's response in the NEXT turn.
        3. ONLY call this tool IF AND ONLY IF the user explicitly says YES / HAAN / SURE / OK.
        4. If the user says NO, DO NOT call this tool.

        Args:
            customer_name: The name of the customer needing human assistance.
            category: Category of issue (e.g. "dispute", "bulk_order", "unlisted_product").
            summary: Short, clear summary of what happened and what was checked (DO NOT include sensitive info like PINs, OTPs, card details).
            urgency: Urgency level ('low', 'medium', 'high', 'urgent').
        """
        self._tools_used.append("create_escalation")
        import json
        actual_user_id = self._user_id or "demo_customer_1"
        ticket_result = create_escalation_ticket(
            user_id=actual_user_id,
            customer_name=customer_name,
            category=category,
            summary=summary,
            urgency=urgency,
        )
        logger.info(f"🚨 Human Help Ticket Created: {ticket_result}")
        return json.dumps(ticket_result, ensure_ascii=False)


server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()
    init_db()
    logger.info("DukaanSaathi database initialized")


server.setup_fnc = prewarm


def format_facts_for_speech(facts: dict) -> str:
    if not facts:
        return "आप पहले भी दुकान से सामान ले चुके हैं"
    parts = []
    for k, v in facts.items():
        val_str = ", ".join(v) if isinstance(v, list) else str(v)
        if "order" in k.lower() or k == "past_orders":
            parts.append(f"पिछली बार आपने {val_str} की बात की थी")
        elif "delivery" in k.lower() or "slot" in k.lower():
            parts.append(f"आपकी डिलीवरी {val_str} को चाहिए थी")
        elif k.lower() in ("name", "user_id", "language_preference"):
            continue
        else:
            parts.append(f"{k} {val_str}")
    return " और ".join(parts) if parts else "आपकी पुरानी बातें याद हैं"


@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):
    import time
    import uuid

    call_id = f"call_{uuid.uuid4().hex[:8]}"
    start_time = time.time()
    tools_used = []

    # Logging setup
    ctx.log_context_fields = {
        "room": ctx.room.name,
        "call_id": call_id,
    }

    # Set up a voice AI pipeline using Murf Falcon, Gemini, Deepgram, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text: Deepgram Nova-3 with multilingual support
        stt=deepgram.STT(model="nova-3", language="multi"),
        # LLM: Google Gemini
        llm=google.LLM(
            model="gemini-3.5-flash-lite",
        ),
        # Text-to-speech: Murf Falcon with Hindi voice
        tts=murf.TTS(
            voice="Anisha",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
        ),
        # VAD and turn detection for natural conversation flow
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    # Join the room and connect to the user
    await ctx.connect()

    # Safely wait for the caller participant to be present in the room
    participant = await ctx.wait_for_participant()
    user_id = participant.identity
    logger.info(f"Participant connected with identity: {user_id}")

    # Parse metadata from dispatch job or room or participant attributes
    import json
    metadata_str = getattr(ctx.job, "metadata", "") or getattr(ctx.room, "metadata", "") or "{}"
    try:
        job_meta = json.loads(metadata_str) if isinstance(metadata_str, str) else {}
    except Exception:
        job_meta = {}

    call_direction = job_meta.get("call_direction") or participant.attributes.get("call_direction", "inbound")
    call_reason = job_meta.get("call_reason") or participant.attributes.get("call_reason", "")
    customer_name = job_meta.get("customer_name") or participant.attributes.get("customer_name", "Customer")

    is_outbound = call_direction == "outbound" or "outbound" in ctx.room.name.lower()
    channel = "sip_outbound" if is_outbound else "browser"

    # Record call start in SQLite analytics database
    record_call_start(call_id=call_id, user_id=user_id, customer_name=customer_name, channel=channel)
    logger.info(f"📊 Call Analytics Started: call_id={call_id}, user={user_id}, channel={channel}")

    if is_outbound:
        # ── OUTBOUND CALL GREETING (Day 6 Requirement) ──────────────────────
        logger.info(f"📞 OUTBOUND CALL active for {customer_name} (Reason: {call_reason})")

        outbound_opening = (
            f"OUTBOUND CALL IN PROGRESS — THIS IS AN OUTBOUND CALL TO {customer_name}.\n\n"
            f"INSTRUCTION:\n"
            f"Your VERY FIRST SENTENCE MUST be the outbound greeting in Devanagari Hindi:\n"
            f"'नमस्ते {customer_name} जी! मैं दुकानसाथी बोल रही हूँ, शर्मा जनरल स्टोर, लक्ष्मी नगर की तरफ से। "
            f"आपके पिछले ऑर्डर के हिसाब से शायद आटा या तेल खत्म हो रहा होगा, तो याद दिलाने के लिए कॉल किया है। "
            f"अगर आप यह कॉल नहीं चाहते तो बस बोलिए \"मुझे कॉल मत करो\" और मैं आगे से कॉल नहीं करूँगी।'\n\n"
            f"After saying this opening sentence, ask if they would like to check prices or order anything today."
        )
        greeting_instruction = outbound_opening

    else:
        # ── INBOUND CALL GREETING ───────────────────────────────────────────
        customer_info = lookup_customer(user_id)

        if customer_info:
            logger.info(f"Returning customer found: {customer_info['name']}")
            facts_summary = format_facts_for_speech(customer_info.get("facts", {}))
            greeting_instruction = (
                f"CRITICAL OVERRIDE - RETURNING CUSTOMER DETECTED!\n"
                f"Customer Name: {customer_info['name']}\n"
                f"Saved Memory Context: {facts_summary}\n\n"
                f"IMPORTANT VOICE INSTRUCTIONS:\n"
                f"1. Your VERY FIRST SENTENCE MUST greet {customer_info['name']} BY NAME in Devanagari script (Hindi).\n"
                f"2. DO NOT output code formatting, dictionary keys, or brackets (never say 'past_orders:' or 'preferred_delivery_slot:').\n"
                f"3. Speak naturally like a local shopkeeper.\n"
                f"Example opening: 'नमस्ते {customer_info['name']} जी! शर्मा जनरल स्टोर में आपका फिर से स्वागत है। {facts_summary}। आज बताइए, आपकी क्या मदद करूँ?'"
            )
        else:
            logger.info(f"New customer connected: {user_id}")
            greeting_instruction = (
                f"NEW CUSTOMER: This caller is visiting for the first time (User ID: '{user_id}').\n"
                f"INSTRUCTION: Greet them as DukaanSaathi representing Sharma General Store in Laxmi Nagar. "
                f"Say: 'नमस्ते! मैं हूँ दुकानसाथी, शर्मा जनरल स्टोर की तरफ से। आपको किसी प्रोडक्ट के बारे में जानना है, स्टोर की टाइमिंग चाहिए, या कुछ और मदद चाहिए? बताइए, मैं हूँ आपके लिए!' "
                f"If they share their name or preferences, ask for consent before calling save_customer."
            )

    # Function to save final call analytics on disconnect
    def finalize_call_analytics():
        duration = int(time.time() - start_time)
        unique_tools = list(set(tools_used))
        if unique_tools:
            status = "successful"
            outcome_reason = f"Completed inquiry ({', '.join(unique_tools)})"
        elif duration >= 5:
            status = "successful"
            outcome_reason = "Completed voice conversation / inquiry"
        else:
            status = "failed"
            outcome_reason = "Early hangup / abandoned call (<5s)"

        record_call_end(
            call_id=call_id,
            status=status,
            outcome_reason=outcome_reason,
            tools_used=unique_tools,
            duration_seconds=duration,
        )
        logger.info(f"📊 Call Finalized: call_id={call_id}, status={status}, duration={duration}s, tools={unique_tools}")

    # Listen for participant disconnect
    ctx.room.on("participant_disconnected", lambda p: finalize_call_analytics())

    # Start the session with the Local Commerce assistant
    await session.start(
        agent=Assistant(user_id=user_id, custom_instructions=greeting_instruction, tools_used_list=tools_used),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if params.participant.kind
                    == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC()
                ),
            ),
        ),
    )

    # Speak the initial greeting out loud immediately when connected
    await session.generate_reply()



if __name__ == "__main__":
    cli.run_app(server)
