package com.arvind.mobilemealscenter.navigation

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.navArgument
import androidx.navigation.compose.navigation
import com.arvind.mobilemealscenter.view.auth.*
import com.arvind.mobilemealscenter.view.customer.*
import com.arvind.mobilemealscenter.view.rider.*

@Composable
fun Navigation(navController: NavHostController) {

    NavHost(
        navController = navController,
        startDestination = Screen.WelcomeScreen.route,
        modifier = Modifier.fillMaxSize()
    ) {

        // Welcome Screen
        composable(Screen.WelcomeScreen.route) {
            WelcomeScreen(navController)
        }
        
        // User Type Selection
        composable(Screen.UserTypeScreen.route) {
            UserTypeScreen(navController)
        }
        
        // Authentication Screens
        composable(Screen.CustomerLoginScreen.route) {
            CustomerLoginScreen(navController)
        }
        
        composable(Screen.RiderLoginScreen.route) {
            RiderLoginScreen(navController)
        }
        
        composable(Screen.RiderRegistrationScreen.route) {
            RiderRegistrationScreen(navController)
        }
        
        composable(Screen.RiderApprovalPendingScreen.route) {
            RiderApprovalPendingScreen(navController)
        }
        
        // Legacy Screens (keeping for compatibility)
        composable(Screen.LoginScreen.route) {
            CustomerLoginScreen(navController)
        }
        
        composable(Screen.CreateAccountScreen.route) {
            RiderRegistrationScreen(navController)
        }

        composable(Screen.OtpVerifyScreen.route) {
            OtpVerifyScreen(navController)
        }
        
        // Customer Screens
        composable(Screen.CustomerHomeScreen.route) {
            CustomerHomeScreen(navController)
        }
        
        composable(Screen.CustomerRestaurantsScreen.route) {
            CustomerHomeScreen(navController) // Reuse home screen for now
        }
        
        composable("customer_restaurant_detail_screen/{restaurantId}") {
            val restaurantId = it.arguments?.getString("restaurantId")
            CustomerHomeScreen(navController) // Will implement detail screen later
        }
        
        composable(Screen.CustomerOrdersScreen.route) {
            CustomerHomeScreen(navController) // Will implement orders screen later
        }
        
        composable("customer_track_order_screen/{orderId}") {
            val orderId = it.arguments?.getString("orderId")
            CustomerTrackOrderScreen(navController, orderId ?: "")
        }
        
        composable(Screen.CustomerProfileScreen.route) {
            CustomerHomeScreen(navController) // Will implement customer profile later
        }
        
        // Rider Screens
        composable(Screen.RiderHomeScreen.route) {
            RiderHomeScreen(navController)
        }
        
        composable(Screen.RiderAvailableOrdersScreen.route) {
            RiderHomeScreen(navController) // Will implement available orders later
        }
        
        composable(Screen.RiderActiveOrdersScreen.route) {
            RiderHomeScreen(navController) // Will implement active orders later
        }
        
        composable("rider_order_detail_screen/{assignmentId}") {
            val assignmentId = it.arguments?.getString("assignmentId")
            RiderHomeScreen(navController) // Will implement order detail later
        }
        
        composable(Screen.RiderDeliveriesScreen.route) {
            RiderHomeScreen(navController) // Will implement deliveries screen later
        }
        
        composable(Screen.RiderProfileScreen.route) {
            RiderProfileScreen(navController)
        }
        
        // Common Screens
        composable(Screen.SearchScreen.route) {
            SearchScreen(navController)
        }
        
        composable(Screen.SettingsScreen.route) {
            ProfileScreen(navController) // Reuse legacy screen
        }
        
        // Legacy Screens (keeping for compatibility)
        composable(Screen.HomeScreen.route) {
            CustomerHomeScreen(navController)
        }
        
        composable(Screen.FavoriteScreen.route) {
            FavoriteScreen(navController)
        }
        
        composable(Screen.OrderScreen.route) {
            OrderScreen(navController)
        }

        composable(Screen.ProfileScreen.route) {
            ProfileScreen(navController)
        }


    }

}