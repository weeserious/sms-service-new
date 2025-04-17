import jwt 
import requests
import sys
from functools import wraps
from django.http import JsonResponse
from django.conf import settings
import os
import json
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import base64

def is_test_environment():
    return 'test' in sys.argv

def get_token_auth_header(request):
    """Extract the token from the Authorization header"""
    auth = request.headers.get('Authorization', None)
    if not auth:
        return None

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        return None

    if len(parts) == 1 or len(parts) > 2:
        return None

    token = parts[1]
    return token

def requires_auth(f):
    """Decorator to validate access tokens"""
    @wraps(f)
    def decorated(request, *args, **kwargs):
        # Skip auth in test environment or when explicitly exempted
        if is_test_environment() or (settings.DEBUG and os.environ.get('EXEMPT_VIEWS_FROM_LOGIN') == 'True'):
            return f(request, *args, **kwargs)
            
        token = get_token_auth_header(request)
        if not token:
            return JsonResponse({"error": "Authorization header is missing"}, status=401)
            
        try:
            jwks_url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
            jwks_response = requests.get(jwks_url)
            jwks = jwks_response.json()
            
            header = jwt.get_unverified_header(token)
            
            rsa_key = None
            for key in jwks['keys']:
                if key['kid'] == header['kid']:
                    rsa_key = jwk_to_pem(key)
                    break
            
            if not rsa_key:
                return JsonResponse({"error": "Key not found"}, status=401)
                
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=['RS256'],
                audience=settings.API_IDENTIFIER,
                issuer=f"https://{settings.AUTH0_DOMAIN}/"
            )
            
            return f(request, *args, **kwargs)
            
        except jwt.exceptions.ExpiredSignatureError:
            return JsonResponse({"error": "Token has expired"}, status=401)
        except jwt.exceptions.InvalidTokenError:
            return JsonResponse({"error": "Invalid token"}, status=401)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=401)
             
    return decorated

def jwk_to_pem(jwk):
    """Convert a JWK key to PEM format"""
    modulus = base64_to_int(jwk['n'])
    exponent = base64_to_int(jwk['e'])
    
    public_numbers = RSAPublicNumbers(exponent, modulus)
    
    public_key = public_numbers.public_key(default_backend())
    
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

def base64_to_int(value):
    """Convert base64 URL encoded value to integer"""
    value += '=' * (4 - len(value) % 4)
    
    value = value.replace('-', '+').replace('_', '/')
    
    decoded = base64.b64decode(value)
    return int.from_bytes(decoded, byteorder='big')