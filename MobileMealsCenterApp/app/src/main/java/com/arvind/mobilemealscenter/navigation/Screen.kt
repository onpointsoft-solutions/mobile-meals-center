package com.arvind.mobilemealscenter.navigation

sealed class Screen(val route: String) {
    // Authentication screens
    object WelcomeScreen : Screen("welcome_screen")
    object CustomerLoginScreen : Screen("customer_login_screen")
    object RiderLoginScreen : Screen("rider_login_screen")
    object RiderRegistrationScreen : Screen("rider_registration_screen")
    object RiderApprovalPendingScreen : Screen("rider_approval_pending_screen")
    object CreateAccountScreen : Screen("create_account_screen")
    object OtpVerifyScreen : Screen("otp_verify_screen")
    object ForgotPasswordScreen : Screen("forgot_password_screen")
    
    // User type selection
    object UserTypeScreen : Screen("user_type_screen")
    
    // Customer screens
    object CustomerHomeScreen : Screen("customer_home_screen")
    object CustomerRestaurantsScreen : Screen("customer_restaurants_screen")
    object CustomerRestaurantDetailScreen : Screen("customer_restaurant_detail_screen")
    object CustomerOrdersScreen : Screen("customer_orders_screen")
    object CustomerTrackOrderScreen : Screen("customer_track_order_screen")
    object CustomerProfileScreen : Screen("customer_profile_screen")
    
    // Rider screens
    object RiderHomeScreen : Screen("rider_home_screen")
    object RiderAvailableOrdersScreen : Screen("rider_available_orders_screen")
    object RiderActiveOrdersScreen : Screen("rider_active_orders_screen")
    object RiderOrderDetailScreen : Screen("rider_order_detail_screen")
    object RiderDeliveriesScreen : Screen("rider_deliveries_screen")
    object RiderProfileScreen : Screen("rider_profile_screen")
    
    // Common screens
    object SearchScreen : Screen("search_screen")
    object SettingsScreen : Screen("settings_screen")

}
