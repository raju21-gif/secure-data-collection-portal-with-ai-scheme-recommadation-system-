from fastapi import Request
from twilio.twiml.messaging_response import MessagingResponse
from ai_engine import get_ai_response

async def handle_twilio_message(request: Request):
    """
    Handles incoming WhatsApp messages from Twilio.
    """
    # Parse form data from Twilio
    form_data = await request.form()
    sender_id = form_data.get('From')
    message_body = form_data.get('Body')

    print(f"Twilio Message from {sender_id}: {message_body}")

    # Generate AI Response
    ai_reply = get_ai_response(message_body, context="User is chatting via WhatsApp (Twilio).")

    # Create TwiML Response
    resp = MessagingResponse()
    resp.message(ai_reply)

    from fastapi import Response
    return Response(content=str(resp), media_type="application/xml")
