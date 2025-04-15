import africastalking
from django.conf import settings

def send_order_notification(phone_number, customer_name, item, amount):
    username = getattr(settings, 'AT_USERNAME', 'sandbox')
    api_key = getattr(settings, 'AT_API_KEY', 'your-api-key')
    sender = getattr(settings, 'SMS_SENDER', '12345')
    
    africastalking.initialize(username=username, api_key=api_key)
    sms = africastalking.SMS
    
    message = f"Hello {customer_name}, your order for {item} with amount ${amount} has been received. Thank you!"
    
    recipient = phone_number
    if recipient.startswith('+'):
        recipient = recipient[1:]
    
    try:
        response = sms.send(
            message=message,
            recipients=[recipient],
            sender_id=sender
        )
        
        return {
            "success": True,
            "message_id": response.get("SMSMessageData", {}).get("Recipients", [{}])[0].get("messageId")
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }