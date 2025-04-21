from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
import json
import requests
import sys


class AuthTests(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_is_test_environment(self):
        from sms_service.auth import is_test_environment
        
        original_argv = sys.argv
        sys.argv = ['manage.py', 'test']
        self.assertTrue(is_test_environment())
        
        sys.argv = ['manage.py', 'runserver']
        self.assertFalse(is_test_environment())
        
        sys.argv = original_argv
    
    def test_token_header_extraction(self):
        from sms_service.auth import get_token_auth_header
        
        request = self.client.request().wsgi_request
        request.headers = {'Authorization': 'Bearer test-token'}
        
        token = get_token_auth_header(request)
        self.assertEqual(token, 'test-token')
        
        request.headers = {'Authorization': 'Basic test-token'}
        token = get_token_auth_header(request)
        self.assertIsNone(token)
        
        request.headers = {}
        token = get_token_auth_header(request)
        self.assertIsNone(token)
    
    @patch('requests.post')
    def test_token_generation(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'access_token': 'test-token',
            'expires_in': 86400,
            'token_type': 'Bearer'
        }
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        response = self.client.post(reverse('generate-token'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)['access_token'], 'test-token')
    
    @patch('requests.post')
    def test_token_generation_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        response = self.client.post(reverse('generate-token'))
        
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.content)['error'], 'Connection refused')
    
    @patch('sms_service.auth_middleware.Auth0TokenMiddleware._get_valid_token')
    def test_middleware_adds_token(self, mock_get_token):
        mock_get_token.return_value = 'middleware-token'
        
        with patch('sms_service.auth_middleware.is_test_environment', return_value=False):
            response = self.client.get('/api/some-endpoint/')
            
        self.assertEqual(response.status_code, 404)  # 404 because endpoint doesn't exist
        
    @patch('sms_service.auth_middleware.Auth0TokenMiddleware._get_valid_token')
    def test_middleware_token_failure(self, mock_get_token):
        mock_get_token.return_value = None
        
        with patch('sms_service.auth_middleware.is_test_environment', return_value=False):
            response = self.client.get('/api/some-endpoint/')
            
        self.assertEqual(response.status_code, 500)
        self.assertEqual(json.loads(response.content)['error'], 'Failed to acquire access token')
    
    def test_middleware_bypass_for_paths(self):
        with patch('sms_service.auth_middleware.is_test_environment', return_value=False):
            response = self.client.get('/oidc/callback/')
            self.assertIn(response.status_code, [302, 404])
            
            response = self.client.get('/admin/')
            self.assertEqual(response.status_code, 302)  
            
            response = self.client.options('/api/some-endpoint/')
            self.assertEqual(response.status_code, 404)

    def test_jwk_to_pem_conversion(self):
        from sms_service.auth import jwk_to_pem
        
        test_jwk = {
            "kty": "RSA",
            "n": "0vx7agoebGcQSuuPiLJXZptN9nndrQmbXEps2aiAFbWhM78LhWx4cbbfAAtVT86zwu1RK7aPFFxuhDR1L6tSoc_BJECPebWKRXjBZCiFV4n3oknjhMstn64tZ_2W-5JsGY4Hc5n9yBXArwl93lqt7_RN5w6Cf0h4QyQ5v-65YGjQR0_FDW2QvzqY368QQMicAtaSqzs8KJZgnYb9c7d0zgdAZHzu6qMQvRL5hajrn1n91CbOpbISD08qNLyrdkt-bFTWhAI4vMQFh6WeZu0fM4lFd2NcRwr3XPksINHaQ-G_xBniIqbw0Ls1jF44-csFCur-kEgU8awapJzKnqDKgw",
            "e": "AQAB"
        }
        
        pem = jwk_to_pem(test_jwk)
        
        # Verify it's a PEM format
        self.assertTrue(pem.startswith(b'-----BEGIN PUBLIC KEY-----'))
        self.assertTrue(pem.endswith(b'-----END PUBLIC KEY-----\n'))

    def test_middleware_token_refresh(self):
        from sms_service.auth_middleware import Auth0TokenMiddleware
        import time
        
        Auth0TokenMiddleware._token = "expired-token"
        Auth0TokenMiddleware._token_expiry = time.time() - 100 
        
        with patch.object(Auth0TokenMiddleware, '_fetch_new_token') as mock_fetch:
            mock_fetch.return_value = {"access_token": "new-refreshed-token", "expires_in": 3600}
            
            token = Auth0TokenMiddleware._get_valid_token()
            
            self.assertEqual(token, "new-refreshed-token")
            mock_fetch.assert_called_once()        