package com.onpointinfo.mobimeals.data.models

import com.google.gson.annotations.SerializedName

data class RiderProfile(
    @SerializedName("id")
    val id: String,
    
    @SerializedName("user")
    val user: User,
    
    @SerializedName("id_number")
    val idNumber: String,
    
    @SerializedName("vehicle_type")
    val vehicleType: String,
    
    @SerializedName("vehicle_number")
    val vehicleNumber: String = "",
    
    @SerializedName("license_number")
    val licenseNumber: String = "",
    
    @SerializedName("phone")
    val phone: String,
    
    @SerializedName("is_online")
    val isOnline: Boolean = false,
    
    @SerializedName("approval_status")
    val approvalStatus: String,
    
    @SerializedName("current_location")
    val currentLocation: Location? = null,
    
    @SerializedName("total_deliveries")
    val totalDeliveries: Int = 0,
    
    @SerializedName("total_earnings")
    val totalEarnings: Double = 0.0,
    
    @SerializedName("rating")
    val rating: Float = 0.0f,
    
    @SerializedName("created_at")
    val createdAt: String
)

data class User(
    @SerializedName("id")
    val id: String,
    
    @SerializedName("username")
    val username: String,
    
    @SerializedName("first_name")
    val firstName: String = "",
    
    @SerializedName("last_name")
    val lastName: String = "",
    
    @SerializedName("email")
    val email: String = "",
    
    @SerializedName("user_type")
    val userType: String
)

data class Location(
    @SerializedName("latitude")
    val latitude: Double,
    
    @SerializedName("longitude")
    val longitude: Double
)

data class DeliveryAssignment(
    @SerializedName("id")
    val id: String,
    
    @SerializedName("order")
    val order: Order,
    
    @SerializedName("rider")
    val rider: RiderProfile,
    
    @SerializedName("status")
    val status: String,
    
    @SerializedName("assigned_at")
    val assignedAt: String,
    
    @SerializedName("picked_up_at")
    val pickedUpAt: String? = null,
    
    @SerializedName("delivered_at")
    val deliveredAt: String? = null,
    
    @SerializedName("delivery_notes")
    val deliveryNotes: String = ""
)

data class ApiResponse(
    @SerializedName("success")
    val success: Boolean,
    
    @SerializedName("message")
    val message: String,
    
    @SerializedName("data")
    val data: Any? = null
)

data class EarningsData(
    @SerializedName("today_earnings")
    val todayEarnings: Double = 0.0,
    
    @SerializedName("week_earnings")
    val weekEarnings: Double = 0.0,
    
    @SerializedName("month_earnings")
    val monthEarnings: Double = 0.0,
    
    @SerializedName("total_earnings")
    val totalEarnings: Double = 0.0,
    
    @SerializedName("total_deliveries")
    val totalDeliveries: Int = 0,
    
    @SerializedName("average_rating")
    val averageRating: Float = 0.0f
)
