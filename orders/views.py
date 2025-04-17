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

@csrf_exempt
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
    return JsonResponse(data, safe=False)

@csrf_exempt
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
    return JsonResponse(data)

@csrf_exempt
@requires_auth
def order_create(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        customer_id = data.get('customer_id')
        item = data.get('item')
        amount = data.get('amount')
        
        if not all([customer_id, item, amount]):
            return JsonResponse({'error': 'All fields are required'}, status=400)
        
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return JsonResponse({'error': f"Customer with ID {customer_id} does not exist"}, status=400)
        
        try:
            if isinstance(amount, str):
                amount = amount.replace(',', '')
            amount = Decimal(amount)
        except:
            return JsonResponse({'error': 'Amount must be a valid number'}, status=400)
        
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
        
        return JsonResponse({
            'id': order.id,
            'customer_id': order.customer.id,
            'customer_name': order.customer.name,
            'item': order.item,
            'amount': str(order.amount),
            'order_time': order.order_time.isoformat()
        }, status=201)
        
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)

@csrf_exempt
@requires_auth
def order_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'PUT':
        data = json.loads(request.body)
        
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
                return JsonResponse({'error': 'Amount must be a valid number'}, status=400)
        
        order.save()
        
        return JsonResponse({
            'id': order.id,
            'customer_id': order.customer.id,
            'customer_name': order.customer.name,
            'item': order.item,
            'amount': str(order.amount),
            'order_time': order.order_time.isoformat()
        })
        
    return JsonResponse({'error': 'Only PUT method allowed'}, status=405)

@csrf_exempt
@requires_auth
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'DELETE':
        order.delete()
        return JsonResponse({}, status=204)
        
    return JsonResponse({'error': 'Only DELETE method allowed'}, status=405)