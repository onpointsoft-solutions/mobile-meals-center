package com.onpointinfo.mobimeals.network

import com.onpointinfo.mobimeals.data.models.*
import retrofit2.Response
import retrofit2.http.*
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
