from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db import transaction
from .models import Order
from customers.models import Customer
from .sms import send_order_notification
import json
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from sms_service.auth import requires_auth
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view
from rest_framework.response import Response

@swagger_auto_schema(
    method='get',
    operation_description="Get a list of all orders",
    responses={
        200: openapi.Response(
            description="Successful operation",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'customer_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'customer_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'item': openapi.Schema(type=openapi.TYPE_STRING),
                        'amount': openapi.Schema(type=openapi.TYPE_STRING),
                        'order_time': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                    }
                )
            )
        ),
        401: openapi.Response(description="Unauthorized")
    }
)
@api_view(['GET'])
@requires_auth
def order_list(request):
    orders = Order.objects.all()
    data = []
    for order in orders:
        data.append({
            'id': order.id,
            'customer_id': order.customer.id,
            'customer_name': order.customer.name,
            'item': order.item,
            'amount': str(order.amount),
            'order_time': order.order_time.isoformat()
        })
    return Response(data)

@swagger_auto_schema(
    method='get',
    operation_description="Get details of a specific order",
    responses={
        200: openapi.Response(
            description="Successful operation",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'customer_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'customer_name': openapi.Schema(type=openapi.TYPE_STRING),
                    'item': openapi.Schema(type=openapi.TYPE_STRING),
                    'amount': openapi.Schema(type=openapi.TYPE_STRING),
                    'order_time': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                }
            )
        ),
    }
)
@api_view(['GET'])
@requires_auth
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    data = {
        'id': order.id,
        'customer_id': order.customer.id,
        'customer_name': order.customer.name,
        'item': order.item,
        'amount': str(order.amount),
        'order_time': order.order_time.isoformat()
    }
    return Response(data)

@swagger_auto_schema(
    method='post',
    operation_description="Create a new order",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['customer_id', 'item', 'amount'],
        properties={
            'customer_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'item': openapi.Schema(type=openapi.TYPE_STRING),
            'amount': openapi.Schema(type=openapi.TYPE_STRING, description="Decimal amount (can include comma as thousand separator)"),
        }
    ),
    responses={
        201: openapi.Response(
            description="Order created successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'customer_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'customer_name': openapi.Schema(type=openapi.TYPE_STRING),
                    'item': openapi.Schema(type=openapi.TYPE_STRING),
                    'amount': openapi.Schema(type=openapi.TYPE_STRING),
                    'order_time': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                }
            )
        )
    }
)
@api_view(['POST'])
@requires_auth
def order_create(request):
    if request.method == 'POST':
        data = request.data
        
        customer_id = data.get('customer_id')
        item = data.get('item')
        amount = data.get('amount')
        
        if not all([customer_id, item, amount]):
            return Response({'error': 'All fields are required'}, status=400)
        
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': f"Customer with ID {customer_id} does not exist"}, status=400)
        
        try:
            if isinstance(amount, str):
                amount = amount.replace(',', '')
            amount = Decimal(amount)
        except:
            return Response({'error': 'Amount must be a valid number'}, status=400)
        
        with transaction.atomic():
            order = Order.objects.create(
                customer=customer,
                item=item,
                amount=amount
            )
            
            send_order_notification(
                customer.phone,
                customer.name,
                order.item,
                str(order.amount)
            )
        
        return Response({
            'id': order.id,
            'customer_id': order.customer.id,
            'customer_name': order.customer.name,
            'item': order.item,
            'amount': str(order.amount),
            'order_time': order.order_time.isoformat()
        }, status=201)

@swagger_auto_schema(
    method='put',
    operation_description="Update an existing order",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'item': openapi.Schema(type=openapi.TYPE_STRING),
            'amount': openapi.Schema(type=openapi.TYPE_STRING, description="Decimal amount (can include comma as thousand separator)"),
        }
    ),
    responses={
        200: openapi.Response(
            description="Order updated successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'customer_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'customer_name': openapi.Schema(type=openapi.TYPE_STRING),
                    'item': openapi.Schema(type=openapi.TYPE_STRING),
                    'amount': openapi.Schema(type=openapi.TYPE_STRING),
                    'order_time': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                }
            )
        ),
        
    }
)
@api_view(['PUT'])
@requires_auth
def order_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'PUT':
        data = request.data
        
        item = data.get('item')
        amount = data.get('amount')
        
        if item:
            order.item = item
        
        if amount:
            try:
                if isinstance(amount, str):
                    amount = amount.replace(',', '')
                order.amount = Decimal(amount)
            except:
                return Response({'error': 'Amount must be a valid number'}, status=400)
        
        order.save()
        
        return Response({
            'id': order.id,
            'customer_id': order.customer.id,
            'customer_name': order.customer.name,
            'item': order.item,
            'amount': str(order.amount),
            'order_time': order.order_time.isoformat()
        })

@swagger_auto_schema(
    method='delete',
    operation_description="Delete an order",
    responses={
        204: openapi.Response(description="Order deleted successfully"),
        401: openapi.Response(description="Unauthorized"),
        404: openapi.Response(description="Order not found"),
        405: openapi.Response(description="Method not allowed")
    }
)
@api_view(['DELETE'])
@requires_auth
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'DELETE':
        order.delete()
        return Response(status=204)