import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def generate_token(request):
    
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
        return JsonResponse(response.json())
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)