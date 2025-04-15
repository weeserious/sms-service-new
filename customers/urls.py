from django.urls import path
from . import views

urlpatterns = [
    path('', views.customer_list, name='customer-list'),
    path('<int:pk>/', views.customer_detail, name='customer-detail'),
    path('create/', views.customer_create, name='customer-create'),
    path('<int:pk>/update/', views.customer_update, name='customer-update'),
    path('<int:pk>/delete/', views.customer_delete, name='customer-delete'),
]