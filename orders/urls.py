from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order-list'),
    path('<int:pk>/', views.order_detail, name='order-detail'),
    path('create/', views.order_create, name='order-create'),
    path('<int:pk>/update/', views.order_update, name='order-update'),
    path('<int:pk>/delete/', views.order_delete, name='order-delete'),
]