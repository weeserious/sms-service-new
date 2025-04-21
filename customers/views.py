from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Customer
import json
from django.views.decorators.csrf import csrf_exempt
from sms_service.auth import requires_auth
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view
from rest_framework.response import Response

@swagger_auto_schema(
    method='get',
    operation_description="Get a list of all customers",
    responses={
        200: openapi.Response(
            description="Successful operation",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'name': openapi.Schema(type=openapi.TYPE_STRING),
                        'code': openapi.Schema(type=openapi.TYPE_STRING),
                        'phone': openapi.Schema(type=openapi.TYPE_STRING),
                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            )
        ),
        401: openapi.Response(description="Unauthorized")
    }
)
@api_view(['GET'])
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
    return Response(data)

@swagger_auto_schema(
    method='get',
    operation_description="Get details of a specific customer",
    responses={
        200: openapi.Response(
            description="Successful operation",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                    'code': openapi.Schema(type=openapi.TYPE_STRING),
                    'phone': openapi.Schema(type=openapi.TYPE_STRING),
                    'email': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        ),
        
    }
)
@api_view(['GET'])
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
    return Response(data)

@swagger_auto_schema(
    method='post',
    operation_description="Create a new customer",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['name', 'code', 'phone', 'email'],
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING),
            'code': openapi.Schema(type=openapi.TYPE_STRING),
            'phone': openapi.Schema(type=openapi.TYPE_STRING),
            'email': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={
        201: openapi.Response(
            description="Customer created successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                    'code': openapi.Schema(type=openapi.TYPE_STRING),
                    'phone': openapi.Schema(type=openapi.TYPE_STRING),
                    'email': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        )
    }
)
@api_view(['POST'])
@requires_auth
def customer_create(request):
    if request.method == 'POST':
        data = request.data
        
        name = data.get('name')
        code = data.get('code')
        phone = data.get('phone')
        email = data.get('email')
        
        if not all([name, code, phone, email]):
            return Response({'error': 'All fields are required'}, status=400)
        
        if Customer.objects.filter(code=code).exists():
            return Response({'error': f"Customer with code '{code}' already exists"}, status=400)
            
        if Customer.objects.filter(email=email).exists():
            return Response({'error': f"Customer with email '{email}' already exists"}, status=400)
        
        customer = Customer.objects.create(
            name=name,
            code=code,
            phone=phone,
            email=email
        )
        
        return Response({
            'id': customer.id,
            'name': customer.name,
            'code': customer.code,
            'phone': customer.phone,
            'email': customer.email
        }, status=201)

@swagger_auto_schema(
    method='put',
    operation_description="Update an existing customer",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'name': openapi.Schema(type=openapi.TYPE_STRING),
            'phone': openapi.Schema(type=openapi.TYPE_STRING),
            'email': openapi.Schema(type=openapi.TYPE_STRING),
        }
    ),
    responses={
        200: openapi.Response(
            description="Customer updated successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                    'code': openapi.Schema(type=openapi.TYPE_STRING),
                    'phone': openapi.Schema(type=openapi.TYPE_STRING),
                    'email': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )
        )
    }
)
@api_view(['PUT'])
@requires_auth
def customer_update(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'PUT':
        data = request.data
        
        name = data.get('name')
        phone = data.get('phone')
        email = data.get('email')
        
        if name:
            customer.name = name
        
        if phone:
            customer.phone = phone
            
        if email:
            if Customer.objects.exclude(id=customer.id).filter(email=email).exists():
                return Response({'error': f"Customer with email '{email}' already exists"}, status=400)
            customer.email = email
        
        customer.save()
        
        return Response({
            'id': customer.id,
            'name': customer.name,
            'code': customer.code,
            'phone': customer.phone,
            'email': customer.email
        })

@swagger_auto_schema(
    method='delete',
    operation_description="Delete a customer",
    responses={
        204: openapi.Response(description="Customer deleted successfully"),
        401: openapi.Response(description="Unauthorized"),
        404: openapi.Response(description="Customer not found"),
        405: openapi.Response(description="Method not allowed")
    }
)
@api_view(['DELETE'])
@requires_auth
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'DELETE':
        customer.delete()
        return Response(status=204)