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
        
    def test_get_customer_detail(self):
        response = self.client.get(
            reverse('customer-detail', args=[self.customer.id]),
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['name'], 'Test Customer')
        self.assertEqual(data['code'], 'TEST123')
        
    def test_create_customer_duplicate_code(self):
        data = {
            "name": "Duplicate Code Customer",
            "code": "TEST123",  # Same as existing customer
            "phone": "0787654321",
            "email": "duplicate@example.com"
        }
        response = self.client.post(
            reverse('customer-create'),
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        
    def test_create_customer_duplicate_email(self):
        data = {
            "name": "Duplicate Email Customer",
            "code": "UNIQUE123",
            "phone": "0787654321",
            "email": "test@example.com"  # Same as existing customer
        }
        response = self.client.post(
            reverse('customer-create'),
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
        
    def test_update_customer(self):
        data = {
            "name": "Updated Customer",
            "phone": "0799887766",
            "email": "updated@example.com"
        }
        response = self.client.put(
            reverse('customer-update', args=[self.customer.id]),
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, 200)
        updated_customer = Customer.objects.get(id=self.customer.id)
        self.assertEqual(updated_customer.name, 'Updated Customer')
        self.assertEqual(updated_customer.email, 'updated@example.com')
        
    def test_delete_customer(self):
        response = self.client.delete(
            reverse('customer-delete', args=[self.customer.id]),
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Customer.objects.count(), 0)