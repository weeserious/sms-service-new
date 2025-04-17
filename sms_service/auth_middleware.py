import time
import requests
import threading
from django.conf import settings
from django.http import JsonResponse

class Auth0TokenMiddleware:
    """
    Middleware that automatically manages Auth0 access tokens.
    
    This middleware handles token acquisition, caching, and refreshing
    for machine-to-machine communications using the OAuth2 client
    credentials flow.
    """
    
    _token = None
    _token_expiry = 0
    _token_lock = threading.RLock()  
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        if 'oidc' in request.path or 'admin' in request.path or 'generate-token' in request.path:
            return self.get_response(request)
            
        if request.method == 'OPTIONS':
            return self.get_response(request)
            
        if request.headers.get('Authorization'):
            return self.get_response(request)
            
        token = self._get_valid_token()
        if not token:
            return JsonResponse({"error": "Failed to acquire access token"}, status=500)
            
        request.META['HTTP_AUTHORIZATION'] = f"Bearer {token}"
        
        return self.get_response(request)
    
    @classmethod
    def _get_valid_token(cls):
        """Get a valid token, refreshing if necessary."""
        with cls._token_lock:
            current_time = time.time()
            
            if cls._token and current_time < cls._token_expiry - 30:
                return cls._token
                
            token_data = cls._fetch_new_token()
            if not token_data:
                return None
                
            cls._token = token_data.get('access_token')
            cls._token_expiry = current_time + token_data.get('expires_in', 86400)
            
            return cls._token
    
    @staticmethod
    def _fetch_new_token():
        """Fetch a new token from Auth0."""
        url = f"https://{settings.AUTH0_DOMAIN}/oauth/token"
        
        payload = {
            "client_id": settings.OIDC_RP_CLIENT_ID,
            "client_secret": settings.OIDC_RP_CLIENT_SECRET,
            "audience": settings.API_IDENTIFIER,
            "grant_type": "client_credentials"
        }
        
        headers = {"content-type": "application/json"}
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching token: {str(e)}")
            return None