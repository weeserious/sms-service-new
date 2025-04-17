from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Customer
import json
from django.views.decorators.csrf import csrf_exempt
from sms_service.auth import requires_auth


@csrf_exempt
@requires_auth
def customer_list(request):
    customers = Customer.objects.all()
    data = []
    for customer in customers:
        data.append({
            'id': customer.id,
            'name': customer.name,
            'code': customer.code,
            'phone': customer.phone,
            'email': customer.email
        })
    return JsonResponse(data, safe=False)

@csrf_exempt
@requires_auth
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    data = {
        'id': customer.id,
        'name': customer.name,
        'code': customer.code,
        'phone': customer.phone,
        'email': customer.email
    }
    return JsonResponse(data)

@csrf_exempt
@requires_auth
def customer_create(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        name = data.get('name')
        code = data.get('code')
        phone = data.get('phone')
        email = data.get('email')
        
        if not all([name, code, phone, email]):
            return JsonResponse({'error': 'All fields are required'}, status=400)
        
        if Customer.objects.filter(code=code).exists():
            return JsonResponse({'error': f"Customer with code '{code}' already exists"}, status=400)
            
        if Customer.objects.filter(email=email).exists():
            return JsonResponse({'error': f"Customer with email '{email}' already exists"}, status=400)
        
        customer = Customer.objects.create(
            name=name,
            code=code,
            phone=phone,
            email=email
        )
        
        return JsonResponse({
            'id': customer.id,
            'name': customer.name,
            'code': customer.code,
            'phone': customer.phone,
            'email': customer.email
        }, status=201)
        
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)

@csrf_exempt
@requires_auth
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'PUT':
        data = json.loads(request.body)
        
        name = data.get('name')
        phone = data.get('phone')
        email = data.get('email')
        
        if name:
            customer.name = name
        
        if phone:
            customer.phone = phone
            
        if email:
            if Customer.objects.exclude(id=customer.id).filter(email=email).exists():
                return JsonResponse({'error': f"Customer with email '{email}' already exists"}, status=400)
            customer.email = email
        
        customer.save()
        
        return JsonResponse({
            'id': customer.id,
            'name': customer.name,
            'code': customer.code,
            'phone': customer.phone,
            'email': customer.email
        })
        
    return JsonResponse({'error': 'Only PUT method allowed'}, status=405)

@csrf_exempt
@requires_auth
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'DELETE':
        customer.delete()
        return JsonResponse({}, status=204)
        
    return JsonResponse({'error': 'Only DELETE method allowed'}, status=405)