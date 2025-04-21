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
        
    def test_order_list(self):
        response = self.client.get(
            reverse('order-list'),
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['item'], 'Test Item')
        
    def test_order_detail(self):
        response = self.client.get(
            reverse('order-detail', args=[self.order.id]),
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['item'], 'Test Item')
        self.assertEqual(data['customer_name'], 'Test Customer')
        
    @patch('orders.sms.send_order_notification')
    def test_invalid_customer_id(self, mock_sms):
        mock_sms.return_value = None
        data = {
            "customer_id": 999,  # Non-existent customer ID
            "item": "Invalid Customer Item",
            "amount": "99.99"
        }
        response = self.client.post(
            reverse('order-create'),
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        
    @patch('orders.sms.send_order_notification')
    def test_invalid_amount(self, mock_sms):
        mock_sms.return_value = None
        data = {
            "customer_id": self.customer.id,
            "item": "Invalid Amount Item",
            "amount": "not-a-number"
        }
        response = self.client.post(
            reverse('order-create'),
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        
    def test_update_order(self):
        data = {
            "item": "Updated Item",
            "amount": "149.99"
        }
        response = self.client.put(
            reverse('order-update', args=[self.order.id]),
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, 200)
        updated_order = Order.objects.get(id=self.order.id)
        self.assertEqual(updated_order.item, 'Updated Item')
        self.assertEqual(updated_order.amount, Decimal('149.99'))
        
    def test_delete_order(self):
        response = self.client.delete(
            reverse('order-delete', args=[self.order.id]),
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Order.objects.count(), 0)