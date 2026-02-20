package com.onpointinfo.mobimeals.network

import com.onpointinfo.mobimeals.data.models.EarningsData
import com.onpointinfo.mobimeals.data.models.RiderProfile
import com.onpointinfo.mobimeals.data.models.DeliveryAssignment
import retrofit2.Response
import retrofit2.http.*

interface RiderApiService {
    
    @GET("/api/riders/profile/")
    suspend fun getRiderProfile(): Response<RiderProfile>
    
    @PUT("/api/riders/profile/")
    suspend fun updateRiderProfile(@Body profile: RiderProfile): Response<RiderProfile>
    
    @POST("/api/riders/toggle-online/")
    suspend fun toggleOnlineStatus(): Response<Map<String, Any>>
    
    @GET("/api/riders/earnings/")
    suspend fun getRiderEarnings(): Response<EarningsData>
    
    @GET("/api/riders/assignments/")
    suspend fun getDeliveryAssignments(): Response<List<DeliveryAssignment>>
    
    @GET("/api/riders/delivery-history/")
    suspend fun getDeliveryHistory(): Response<List<DeliveryAssignment>>
    
    @GET("/api/riders/assignments/{assignment_id}/")
    suspend fun getAssignmentDetails(@Path("assignment_id") assignmentId: String): Response<DeliveryAssignment>
    
    @PUT("/api/riders/assignments/{assignment_id}/status/")
    suspend fun updateAssignmentStatus(
        @Path("assignment_id") assignmentId: String,
        @Body status: Map<String, String>
    ): Response<DeliveryAssignment>
    
    @POST("/api/riders/assignments/{assignment_id}/pickup/")
    suspend fun markAsPickedUp(@Path("assignment_id") assignmentId: String): Response<DeliveryAssignment>
    
    @POST("/api/riders/assignments/{assignment_id}/deliver/")
    suspend fun markAsDelivered(
        @Path("assignment_id") assignmentId: String,
        @Body deliveryData: Map<String, Any>
    ): Response<DeliveryAssignment>
    
    @GET("/api/riders/available-orders/")
    suspend fun getAvailableOrders(): Response<List<Any>> // Replace with Order model when available
    
    @POST("/api/riders/accept-order/")
    suspend fun acceptOrder(@Body orderData: String): Response<DeliveryAssignment>
}
