from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, get_user_model
from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal

from orders.models import Order
from .models import RiderProfile, DeliveryAssignment
from core.utils import get_delivery_fee, get_commission_rate, get_tax_rate
import json


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_online_status(request):
    """Toggle rider's online status"""
    try:
        rider = get_object_or_404(RiderProfile, user=request.user)
        
        # Check if rider is approved and active
        if not rider.is_approved:
            return JsonResponse({
                'error': 'Your account is not approved yet',
                'status': 'pending'
            }, status=403)
        
        if not rider.is_active:
            return JsonResponse({
                'error': 'Your account is suspended',
                'status': 'suspended'
            }, status=403)
        
        # Toggle online status
        rider.is_online = not rider.is_online
        rider.update_last_active()
        
        return JsonResponse({
            'success': True,
            'is_online': rider.is_online,
            'message': f"You are now {'online' if rider.is_online else 'offline'}"
        })
        
    except RiderProfile.DoesNotExist:
        return JsonResponse({
            'error': 'Rider profile not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_rider_profile(request):
    """Get current rider's profile"""
    try:
        rider = get_object_or_404(RiderProfile, user=request.user)
        
        profile_data = {
            'id': str(rider.id),
            'user': {
                'id': rider.user.id,
                'username': rider.user.username,
                'email': rider.user.email,
                'first_name': rider.user.first_name,
                'last_name': rider.user.last_name,
                'phone': getattr(rider.user, 'phone', ''),
                'is_approved': rider.is_approved,
                'approval_status': rider.approval_status,
                'user_type': 'rider'
            },
            'id_number': rider.id_number,
            'vehicle_type': rider.vehicle_type,
            'vehicle_number': rider.vehicle_number,
            'emergency_contact': rider.emergency_contact,
            'bank_account': rider.bank_account,
            'bank_name': rider.bank_name,
            'delivery_areas': rider.delivery_areas,
            'rating': float(rider.rating),
            'total_deliveries': rider.total_deliveries,
            'is_online': rider.is_online,
            'is_active': rider.is_active,
            'created_at': rider.created_at.isoformat(),
            'last_active_at': rider.last_active_at.isoformat() if rider.last_active_at else None
        }
        
        return Response(profile_data)
        
    except RiderProfile.DoesNotExist:
        return Response({
            'error': 'Rider profile not found'
        }, status=404)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_rider_profile(request):
    """Create or update rider profile"""
    try:
        rider, created = RiderProfile.objects.get_or_create(user=request.user)
        
        data = json.loads(request.body)
        
        # Update profile fields
        if 'id_number' in data:
            rider.id_number = data['id_number']
        if 'vehicle_type' in data:
            rider.vehicle_type = data['vehicle_type']
        if 'vehicle_number' in data:
            rider.vehicle_number = data['vehicle_number']
        if 'emergency_contact' in data:
            rider.emergency_contact = data['emergency_contact']
        if 'bank_account' in data:
            rider.bank_account = data['bank_account']
        if 'bank_name' in data:
            rider.bank_name = data['bank_name']
        if 'delivery_areas' in data:
            rider.delivery_areas = data['delivery_areas']
        
        rider.save()
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'profile': {
                'id': str(rider.id),
                'is_approved': rider.is_approved,
                'approval_status': rider.approval_status
            }
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_orders(request):
    """Get orders available for delivery"""
    try:
        rider = get_object_or_404(RiderProfile, user=request.user)
        
        # Check if rider is approved and online
        if not rider.is_approved:
            return Response({
                'error': 'Your account is not approved yet'
            }, status=403)
        
        if not rider.is_online:
            return Response({
                'error': 'You must be online to view available orders'
            }, status=403)
        
        # Get orders that are ready for delivery and not assigned
        available_orders = Order.objects.filter(
            status='ready',
            delivery_assignments__isnull=True
        ).select_related(
            'customer', 'restaurant'
        ).order_by('created_at')
        
        orders_data = []
        for order in available_orders:
            # Calculate delivery fee
            delivery_fee = get_delivery_fee()
            
            orders_data.append({
                'id': order.id,
                'order_number': order.order_number,
                'customer': {
                    'id': order.customer.id,
                    'first_name': order.customer.first_name,
                    'last_name': order.customer.last_name,
                    'phone': getattr(order.customer, 'phone', ''),
                    'email': order.customer.email
                },
                'restaurant': {
                    'id': order.restaurant.id,
                    'name': order.restaurant.name,
                    'address': order.restaurant.address,
                    'phone': getattr(order.restaurant, 'phone', '')
                },
                'delivery_address': order.delivery_address,
                'phone': order.phone,
                'special_instructions': order.special_instructions or '',
                'total_amount': float(order.total_amount),
                'delivery_fee': float(delivery_fee),
                'created_at': order.created_at.isoformat(),
                'estimated_delivery_time': '30-45 minutes'
            })
        
        return Response(orders_data)
        
    except RiderProfile.DoesNotExist:
        return Response({
            'error': 'Rider profile not found'
        }, status=404)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_orders(request):
    """Get rider's active delivery assignments"""
    try:
        rider = get_object_or_404(RiderProfile, user=request.user)
        
        active_assignments = DeliveryAssignment.objects.filter(
            rider=rider,
            status__in=['assigned', 'picked_up', 'delivering']
        ).select_related(
            'order', 'order__customer', 'order__restaurant'
        ).order_by('-assigned_at')
        
        assignments_data = []
        for assignment in active_assignments:
            assignments_data.append({
                'id': str(assignment.id),
                'order': {
                    'id': assignment.order.id,
                    'order_number': assignment.order.order_number,
                    'customer': {
                        'first_name': assignment.order.customer.first_name,
                        'last_name': assignment.order.customer.last_name,
                        'phone': getattr(assignment.order.customer, 'phone', '')
                    },
                    'restaurant': {
                        'name': assignment.order.restaurant.name,
                        'address': assignment.order.restaurant.address
                    },
                    'delivery_address': assignment.order.delivery_address,
                    'total_amount': float(assignment.order.total_amount),
                    'delivery_fee': float(assignment.delivery_fee)
                },
                'status': assignment.status,
                'assigned_at': assignment.assigned_at.isoformat(),
                'picked_up_at': assignment.picked_up_at.isoformat() if assignment.picked_up_at else None,
                'delivery_fee': float(assignment.delivery_fee)
            })
        
        return Response(assignments_data)
        
    except RiderProfile.DoesNotExist:
        return Response({
            'error': 'Rider profile not found'
        }, status=404)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_order(request, order_id):
    """Accept a delivery order"""
    try:
        rider = get_object_or_404(RiderProfile, user=request.user)
        order = get_object_or_404(Order, id=order_id)
        
        # Check if rider is approved and online
        if not rider.is_approved:
            return Response({
                'error': 'Your account is not approved yet'
            }, status=403)
        
        if not rider.is_online:
            return Response({
                'error': 'You must be online to accept orders'
            }, status=403)
        
        # Check if order is still available
        if order.status != 'ready':
            return Response({
                'error': 'Order is no longer available for delivery'
            }, status=400)
        
        # Check if order is already assigned
        if DeliveryAssignment.objects.filter(order=order, status__in=['assigned', 'picked_up', 'delivering']).exists():
            return Response({
                'error': 'Order is already assigned to another rider'
            }, status=400)
        
        # Calculate delivery fee
        delivery_fee = get_delivery_fee()
        
        # Create delivery assignment
        assignment = DeliveryAssignment.objects.create(
            order=order,
            rider=rider,
            status='assigned',
            delivery_fee=delivery_fee
        )
        
        # Update order status
        order.status = 'delivering'
        order.save()
        
        return Response({
            'success': True,
            'assignment': {
                'id': str(assignment.id),
                'order_id': order.id,
                'status': assignment.status,
                'delivery_fee': float(delivery_fee),
                'assigned_at': assignment.assigned_at.isoformat()
            },
            'message': 'Order accepted successfully'
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_delivery_status(request, assignment_id):
    """Update delivery assignment status"""
    try:
        rider = get_object_or_404(RiderProfile, user=request.user)
        assignment = get_object_or_404(DeliveryAssignment, id=assignment_id, rider=rider)
        
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if new_status not in ['picked_up', 'delivering', 'delivered', 'cancelled']:
            return Response({
                'error': 'Invalid status'
            }, status=400)
        
        # Update status
        assignment.status = new_status
        
        if new_status == 'picked_up':
            assignment.mark_picked_up()
        elif new_status == 'delivered':
            assignment.mark_delivered()
        elif new_status == 'cancelled':
            assignment.cancel_assignment(data.get('reason', 'Cancelled by rider'))
        
        assignment.save()
        
        return Response({
            'success': True,
            'status': assignment.status,
            'message': f'Delivery status updated to {assignment.get_status_display()}'
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_rider_earnings(request):
    """Get rider earnings information"""
    try:
        rider = get_object_or_404(RiderProfile, user=request.user)
        
        # Calculate earnings from completed deliveries
        completed_assignments = DeliveryAssignment.objects.filter(
            rider=rider,
            status='delivered'
        )
        
        total_earnings = sum(assignment.delivery_fee for assignment in completed_assignments)
        total_deliveries = completed_assignments.count()
        
        # Calculate earnings for different periods
        from datetime import datetime, timedelta
        
        today = timezone.now().date()
        this_week_start = today - timedelta(days=today.weekday())
        this_month_start = today.replace(day=1)
        
        today_earnings = sum(
            assignment.delivery_fee 
            for assignment in completed_assignments
            if assignment.delivered_at and assignment.delivered_at.date() == today
        )
        
        week_earnings = sum(
            assignment.delivery_fee 
            for assignment in completed_assignments
            if assignment.delivered_at and assignment.delivered_at.date() >= this_week_start
        )
        
        month_earnings = sum(
            assignment.delivery_fee 
            for assignment in completed_assignments
            if assignment.delivered_at and assignment.delivered_at.date() >= this_month_start
        )
        
        return Response({
            'total_earnings': float(total_earnings),
            'total_deliveries': total_deliveries,
            'today_earnings': float(today_earnings),
            'week_earnings': float(week_earnings),
            'month_earnings': float(month_earnings),
            'average_per_delivery': float(total_earnings / total_deliveries) if total_deliveries > 0 else 0.0
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_delivery_history(request):
    """Get rider's complete delivery history"""
    try:
        rider = get_object_or_404(RiderProfile, user=request.user)
        
        # Get all assignments (completed and cancelled)
        assignments = DeliveryAssignment.objects.filter(
            rider=rider
        ).select_related(
            'order', 'order__customer', 'order__restaurant'
        ).order_by('-assigned_at')
        
        history_data = []
        for assignment in assignments:
            history_data.append({
                'id': str(assignment.id),
                'order': {
                    'id': assignment.order.id,
                    'order_number': assignment.order.order_number,
                    'customer': {
                        'first_name': assignment.order.customer.first_name,
                        'last_name': assignment.order.customer.last_name,
                        'phone': getattr(assignment.order.customer, 'phone', '')
                    },
                    'restaurant': {
                        'name': assignment.order.restaurant.name,
                        'address': assignment.order.restaurant.address
                    },
                    'total_amount': float(assignment.order.total_amount)
                },
                'status': assignment.status,
                'delivery_fee': float(assignment.delivery_fee),
                'assigned_at': assignment.assigned_at.isoformat(),
                'picked_up_at': assignment.picked_up_at.isoformat() if assignment.picked_up_at else None,
                'delivered_at': assignment.delivered_at.isoformat() if assignment.delivered_at else None,
                'pickup_notes': assignment.pickup_notes or '',
                'delivery_notes': assignment.delivery_notes or ''
            })
        
        return Response(history_data)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def rider_register(request):
    """API endpoint for rider registration"""
    try:
        data = json.loads(request.body)
        
        # Extract registration data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone = data.get('phone', '')
        
        # Validate required fields
        if not all([username, email, password, first_name, last_name]):
            return JsonResponse({
                'error': 'Missing required fields: username, email, password, first_name, last_name'
            }, status=400)
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'error': 'Username already exists'
            }, status=400)
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'error': 'Email already exists'
            }, status=400)
        
        # Create new user with rider type
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            user_type='rider',
            is_approved=False,  # Riders need approval
            approval_status='pending'
        )
        
        # Create rider profile with minimal required data
        # Note: Additional documents will be required during profile completion
        try:
            # Create a temporary file for placeholder documents
            import tempfile
            import os
            from django.core.files.base import ContentFile
            
            # Create placeholder content for file fields
            placeholder_content = b"Placeholder document - will be updated during profile completion"
            placeholder_file = ContentFile(placeholder_content, "placeholder.txt")
            
            rider_profile = RiderProfile.objects.create(
                user=user,
                id_number="PENDING",  # Will be updated during profile completion
                id_document=placeholder_file,  # Placeholder file
                vehicle_type='motorcycle',  # Default vehicle type
                vehicle_number="PENDING",  # Will be updated during profile completion
                vehicle_document=placeholder_file,  # Placeholder file
                emergency_contact="0000000000",  # Will be updated during profile completion
                bank_account="PENDING",  # Will be updated during profile completion
                bank_name="PENDING",  # Will be updated during profile completion
                delivery_areas=[],  # Empty list initially
                is_active=False  # Inactive until profile is completed and approved
            )
        except Exception as e:
            # If rider profile creation fails, delete the user and return error
            user.delete()
            return JsonResponse({
                'error': f'Failed to create rider profile: {str(e)}'
            }, status=500)
        
        return JsonResponse({
            'success': True,
            'message': 'Registration successful! Please complete your profile with required documents to activate your account.',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'userType': 'rider',
                'is_approved': user.is_approved,
                'approval_status': user.approval_status
            },
            'next_steps': [
                'Complete your profile with personal information',
                'Upload ID document and vehicle documents',
                'Add bank account details for payments',
                'Wait for admin approval'
            ]
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid request data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def rider_login(request):
    """Custom login for riders with approval check"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            return JsonResponse({
                'error': 'Invalid username or password'
            }, status=401)
        
        # Check if user is a rider
        try:
            rider_profile = user.rider_profile
            
            if not rider_profile.is_approved:
                return JsonResponse({
                    'error': 'Your account is not approved yet',
                    'approval_status': rider_profile.approval_status,
                    'message': 'Please wait for admin approval'
                }, status=403)
            
            if not rider_profile.is_active:
                return JsonResponse({
                    'error': 'Your account has been suspended',
                    'message': 'Please contact support'
                }, status=403)
            
            # Login successful
            login(request, user)
            
            return JsonResponse({
                'success': True,
                'token': 'mock_token',  # In production, use JWT
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone': getattr(user, 'phone', ''),
                    'userType': 'rider',
                    'is_approved': rider_profile.is_approved,
                    'approval_status': rider_profile.approval_status
                }
            })
            
        except RiderProfile.DoesNotExist:
            return JsonResponse({
                'error': 'This login is for riders only. Please select the correct user type.'
            }, status=403)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid request data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
