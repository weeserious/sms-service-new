import africastalking
import os
from django.conf import settings

username = settings.AT_USERNAME
api_key = settings.AT_API_KEY


africastalking.initialize(username, api_key)
sms = africastalking.SMS

def send_order_notification(phone_number, customer_name, item, amount):
   
    message = f"Hello {customer_name}, order for {item} has been received. Total: Ksh {amount}. Thank you!"
    
    if not phone_number.startswith('+'):
        phone_number = '+254' + phone_number.lstrip('0')
    
    try:
        response = sms.send(message, [phone_number])
        return response
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        return None