from django.test import TestCase, Client
from django.urls import reverse
import json
from .models import Customer
import os
from dotenv import load_dotenv

load_dotenv()

class CustomerTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = Customer.objects.create(
            name="Test Customer",
            code="TEST123",
            phone="0712345678",
            email="test@example.com"
        )
        
        # Get token from .env
        self.token = os.environ.get('ACCESS_TOKEN', '')
        
    def test_customer_model(self):
        self.assertEqual(self.customer.name, "Test Customer")
        self.assertEqual(self.customer.code, "TEST123")
    
    def test_get_customers(self):
        response = self.client.get(
            reverse('customer-list'),
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_create_customer(self):
        data = {
            "name": "New Customer",
            "code": "NEW123",
            "phone": "0787654321",
            "email": "new@example.com"
        }
        response = self.client.post(
            reverse('customer-create'),
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Customer.objects.count(), 2)