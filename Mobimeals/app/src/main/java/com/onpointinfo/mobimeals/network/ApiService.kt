package com.onpointinfo.mobimeals.network

import com.onpointinfo.mobimeals.data.models.*
import retrofit2.Response
import retrofit2.http.*

interface RiderApiService {
    
    @GET("/riders/profile/")
    suspend fun getRiderProfile(): Response<RiderProfile>
    
    @POST("/riders/profile/create/")
    suspend fun createRiderProfile(@Body profile: RiderProfile): Response<ApiResponse>
    
    @POST("/riders/toggle-online/")
    suspend fun toggleOnlineStatus(): Response<ApiResponse>
    
    @GET("/riders/available-orders/")
    suspend fun getAvailableOrders(): Response<List<Order>>
    
    @GET("/riders/active-orders/")
    suspend fun getActiveOrders(): Response<List<DeliveryAssignment>>
    
    @POST("/riders/accept-order/{order_id}/")
    suspend fun acceptOrder(@Path("order_id") orderId: String): Response<ApiResponse>
    
    @PUT("/riders/update-delivery/{assignment_id}/")
    suspend fun updateDeliveryStatus(
        @Path("assignment_id") assignmentId: String,
        @Body status: Map<String, String>
    ): Response<ApiResponse>
    
    @GET("/riders/earnings/")
    suspend fun getRiderEarnings(): Response<EarningsData>
    
    @GET("/riders/delivery-history/")
    suspend fun getDeliveryHistory(): Response<List<DeliveryAssignment>>
}

interface CustomerApiService {
    
    @GET("/restaurants/")
    suspend fun getRestaurants(@Query("search") search: String? = null): Response<List<Restaurant>>
    
    @GET("/restaurants/{id}/")
    suspend fun getRestaurantDetail(@Path("id") restaurantId: String): Response<Restaurant>
    
    @GET("/orders/customer/")
    suspend fun getCustomerOrders(): Response<List<Order>>
    
    @GET("/orders/{id}/")
    suspend fun getOrderDetail(@Path("id") orderId: String): Response<Order>
    
    @POST("/orders/update-status/")
    suspend fun updateOrderStatus(@Body update: Map<String, String>): Response<ApiResponse>
}

interface AuthApiService {
    
    @POST("/api/riders/login/")
    suspend fun login(@Body credentials: LoginRequest): Response<LoginResponse>
    
    @POST("/api/riders/register/")
    suspend fun register(@Body registration: RiderRegistrationRequest): Response<LoginResponse>
    
    @POST("/accounts/logout/")
    suspend fun logout(): Response<ApiResponse>
    
    @POST("/accounts/refresh/")
    suspend fun refreshToken(@Body token: RefreshTokenRequest): Response<LoginResponse>
    
    @GET("/accounts/user/")
    suspend fun getCurrentUser(): Response<User>
}

data class LoginRequest(
    val username: String,
    val password: String
)

data class RiderRegistrationRequest(
    val username: String,
    val email: String,
    val password: String,
    val first_name: String,
    val last_name: String,
    val phone: String = ""
)

data class LoginResponse(
    val success: Boolean,
    val message: String,
    val access_token: String? = null,
    val refresh_token: String? = null,
    val user: User? = null
)

data class RefreshTokenRequest(
    val refresh: String
)
