# Mobile Meals Center App Setup

## Overview
The MobileMealsCenterApp has been updated to work with the Django backend and support both customers and delivery riders. The app now resembles the web application with appropriate branding and functionality.

## Key Changes Made

### 1. App Rebranding
- **App Name**: Changed from "Foodizone" to "Mobile Meals Center"
- **Package Name**: Updated from `com.arvind.foodizone` to `com.arvind.mobilemealscenter`
- **Theme**: Updated theme references to use MobileMealsCenter

### 2. User Type Support
The app now supports two main user types:

#### Customers
- View restaurants and their menus
- Track order status in real-time
- View order history
- Manage profile

#### Riders
- View available delivery orders
- Accept and manage deliveries
- Track delivery status
- View earnings and delivery history

### 3. New Navigation Structure

#### Authentication Screens
- Welcome Screen
- Login Screen (with user type context)
- Create Account Screen
- OTP Verification
- Forgot Password

#### Customer Screens
- Customer Home Screen (Restaurant browsing)
- Customer Restaurants Screen
- Customer Restaurant Detail Screen
- Customer Orders Screen
- Customer Track Order Screen
- Customer Profile Screen

#### Rider Screens
- Rider Home Screen (Dashboard)
- Rider Available Orders Screen
- Rider Active Orders Screen
- Rider Order Detail Screen
- Rider Deliveries Screen
- Rider Profile Screen

### 4. Backend Integration

#### API Service
- Created `ApiService` interface for Django backend communication
- Implemented endpoints for authentication, restaurants, orders, and rider operations
- Base URL: `https://mobilemealscenter.co.ke/`

#### Data Models
- **User**: Login, registration, and user profile data
- **Restaurant**: Restaurant information and menu items
- **Order**: Order details, status tracking, and items
- **DeliveryAssignment**: Rider-specific delivery data

#### Network Layer
- Retrofit for HTTP requests
- Gson for JSON parsing
- Proper error handling and token management

### 5. Key Features

#### Customer Features
- **Restaurant Browsing**: View all restaurants with search functionality
- **Restaurant Details**: View restaurant info, menu, and ratings
- **Order Tracking**: Real-time order status timeline
- **Order History**: View past orders and details

#### Rider Features
- **Dashboard**: Overview of available and active deliveries
- **Available Orders**: View orders ready for delivery
- **Delivery Management**: Accept, pick up, and complete deliveries
- **Earnings Tracking**: Monitor delivery performance

### 6. UI/UX Improvements
- **Modern Material Design**: Updated to match web application
- **Responsive Layout**: Optimized for different screen sizes
- **Status Indicators**: Visual feedback for order and delivery status
- **Navigation**: User-specific bottom navigation

### 7. Technology Stack
- **Kotlin**: Primary programming language
- **Jetpack Compose**: Modern UI toolkit
- **Retrofit**: HTTP client for API calls
- **Coil**: Image loading library
- **Navigation Compose**: Screen navigation
- **Hilt**: Dependency injection
- **Coroutines**: Asynchronous programming

## Backend API Requirements

The app expects the following Django API endpoints:

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration
- `GET /api/auth/user/` - Get current user

### Restaurants
- `GET /api/restaurants/` - List all restaurants
- `GET /api/restaurants/{id}/` - Get restaurant details
- `GET /api/restaurants/{id}/meals/` - Get restaurant menu
- `GET /api/meals/categories/` - Get meal categories

### Orders
- `GET /api/orders/` - List user orders
- `GET /api/orders/{id}/` - Get order details
- `POST /api/orders/` - Create new order

### Rider Operations
- `GET /api/riders/available-orders/` - Get available delivery orders
- `GET /api/riders/active-orders/` - Get rider's active deliveries
- `POST /api/riders/accept-order/{orderId}/` - Accept a delivery
- `PUT /api/riders/update-delivery/{assignmentId}/` - Update delivery status

## Setup Instructions

### 1. Update Backend URLs
In `RetrofitClient.kt`, update the `BASE_URL` to match your Django server:
```kotlin
private const val BASE_URL = "https://your-domain.com/"
```

### 2. Add API Endpoints
Ensure your Django backend has the required API endpoints as listed above.

### 3. Authentication
Implement proper token-based authentication in the Django backend.

### 4. Build and Run
```bash
./gradlew build
./gradlew installDebug
```

## Current Limitations

1. **Ordering Disabled**: Customers can view restaurants and food but cannot place orders through the app (as requested)
2. **Token Management**: Basic token implementation - needs secure storage
3. **Real-time Updates**: No WebSocket integration for live updates
4. **Offline Support**: Limited offline functionality
5. **Push Notifications**: Not implemented

## Future Enhancements

1. **Real-time Order Tracking**: WebSocket integration
2. **Push Notifications**: Order status updates
3. **Offline Mode**: Cache restaurant data
4. **Payment Integration**: In-app payments
5. **Advanced Rider Features**: Route optimization, earnings analytics
6. **Customer Reviews**: Rating and review system

## Notes

- The app structure is designed to be easily extensible
- All network calls should include proper error handling
- Token management should use Android Keystore for security
- Consider implementing proper logging and analytics
- Test thoroughly with real backend data
