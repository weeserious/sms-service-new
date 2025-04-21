"""
URL configuration for sms_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .token_generator import generate_token
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.http import HttpResponse

def test_view(request):
    return HttpResponse("Django app is working")

schema_view = get_schema_view(
    openapi.Info(
        title="Service API",
        default_version='v1',
        description="SMS Service"
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('test/', test_view, name='test'),
    path('admin/', admin.site.urls),
    path('api/customers/', include('customers.urls')),
    path('api/orders/', include('orders.urls')),
    path('oidc/', include('mozilla_django_oidc.urls')),
    path('api/generate-token/', generate_token, name='generate-token'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]