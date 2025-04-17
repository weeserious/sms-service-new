from django.test import TestCase, Client
from django.urls import reverse
import json
from .models import Order
from customers.models import Customer
from decimal import Decimal
from unittest.mock import patch
import os
from dotenv import load_dotenv

load_dotenv()

class OrderTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = Customer.objects.create(
            name="Test Customer",
            code="TEST123",
            phone="0712345678",
            email="test@example.com"
        )
        self.order = Order.objects.create(
            customer=self.customer,
            item="Test Item",
            amount=Decimal("99.99")
        )
        
        # Get token from .env
        self.token = os.environ.get('ACCESS_TOKEN', '')
    
    def test_order_model(self):
        self.assertEqual(self.order.item, "Test Item")
        self.assertEqual(self.order.amount, Decimal("99.99"))
    
    @patch('orders.sms.send_order_notification')
    def test_create_order(self, mock_sms):
        mock_sms.return_value = None
        data = {
            "customer_id": self.customer.id,
            "item": "New Item",
            "amount": "199.99"
        }
        response = self.client.post(
            reverse('order-create'),
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.count(), 2)
    
    @patch('orders.sms.send_order_notification')
    def test_formatted_amount(self, mock_sms):
        mock_sms.return_value = None
        data = {
            "customer_id": self.customer.id,
            "item": "Formatted Item",
            "amount": "1,234.56"
        }
        response = self.client.post(
            reverse('order-create'),
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, 201)
        new_order = Order.objects.get(item="Formatted Item")
        self.assertEqual(new_order.amount, Decimal("1234.56"))