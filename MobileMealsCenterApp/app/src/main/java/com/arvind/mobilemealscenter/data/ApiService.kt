package com.arvind.mobilemealscenter.data

import com.arvind.mobilemealscenter.model.*
import retrofit2.Response
import retrofit2.http.*

interface ApiService {
    
    // Authentication endpoints
    @POST("/api/auth/login/")
    suspend fun login(@Body loginRequest: LoginRequest): Response<LoginResponse>
    
    @POST("/api/auth/register/")
    suspend fun register(@Body registerRequest: RegisterRequest): Response<User>
    
    @GET("/api/auth/user/")
    suspend fun getCurrentUser(@Header("Authorization") token: String): Response<User>
    
    // Restaurant endpoints
    @GET("/api/restaurants/")
    suspend fun getRestaurants(): Response<List<Restaurant>>
    
    @GET("/api/restaurants/{id}/")
    suspend fun getRestaurant(@Path("id") id: Int): Response<Restaurant>
    
    @GET("/api/restaurants/{id}/meals/")
    suspend fun getRestaurantMeals(@Path("id") id: Int): Response<List<Meal>>
    
    @GET("/api/meals/categories/")
    suspend fun getCategories(): Response<List<Category>>
    
    // Order endpoints
    @GET("/api/orders/")
    suspend fun getOrders(@Header("Authorization") token: String): Response<List<Order>>
    
    @GET("/api/orders/{id}/")
    suspend fun getOrder(@Header("Authorization") token: String, @Path("id") id: Int): Response<Order>
    
    @POST("/api/orders/")
    suspend fun createOrder(@Header("Authorization") token: String, @Body order: Order): Response<Order>
    
    // Rider endpoints
    @GET("/api/riders/profile/")
    suspend fun getRiderProfile(@Header("Authorization") token: String): Response<RiderProfile>
    
    @POST("/api/riders/profile/")
    suspend fun createRiderProfile(@Header("Authorization") token: String, @Body profile: RiderProfile): Response<RiderProfile>
    
    @PUT("/api/riders/profile/")
    suspend fun updateRiderProfile(@Header("Authorization") token: String, @Body profile: RiderProfile): Response<RiderProfile>
    
    @POST("/api/riders/toggle-online/")
    suspend fun toggleOnlineStatus(@Header("Authorization") token: String): Response<Map<String, Any>>
    
    @GET("/api/riders/available-orders/")
    suspend fun getAvailableOrders(@Header("Authorization") token: String): Response<List<Order>>
    
    @GET("/api/riders/active-orders/")
    suspend fun getActiveOrders(@Header("Authorization") token: String): Response<List<DeliveryAssignment>>
    
    @POST("/api/riders/accept-order/{orderId}/")
    suspend fun acceptOrder(@Header("Authorization") token: String, @Path("orderId") orderId: Int): Response<DeliveryAssignment>
    
    @PUT("/api/riders/update-delivery/{assignmentId}/")
    suspend fun updateDeliveryStatus(
        @Header("Authorization") token: String,
        @Path("assignmentId") assignmentId: Int,
        @Body status: Map<String, String>
    ): Response<DeliveryAssignment>
    
    @GET("/api/riders/earnings/")
    suspend fun getRiderEarnings(@Header("Authorization") token: String): Response<Map<String, Any>>
    
    @GET("/api/riders/delivery-history/")
    suspend fun getDeliveryHistory(@Header("Authorization") token: String): Response<List<DeliveryAssignment>>
}
