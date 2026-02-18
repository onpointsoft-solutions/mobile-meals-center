package com.arvind.mobilemealscenter.model

data class User(
    val id: Int,
    val username: String,
    val email: String,
    val firstName: String,
    val lastName: String,
    val phone: String?,
    val userType: String, // "customer", "rider", "restaurant"
    val is_active: Boolean,
    val date_joined: String,
    // Rider-specific fields
    val is_approved: Boolean = false,
    val approval_status: String = "pending", // "pending", "approved", "rejected"
    val rider_profile: RiderProfile? = null
)

data class RiderProfile(
    val id: Int,
    val user: Int,
    val id_number: String?,
    val id_document: String?,
    val vehicle_type: String, // "bicycle", "motorcycle", "car"
    val vehicle_number: String?,
    val vehicle_document: String?,
    val emergency_contact: String?,
    val bank_account: String?,
    val bank_name: String?,
    val delivery_areas: List<String> = emptyList(),
    val rating: Double = 0.0,
    val total_deliveries: Int = 0,
    val is_online: Boolean = false
)

data class LoginRequest(
    val username: String,
    val password: String
)

data class LoginResponse(
    val token: String,
    val user: User
)

data class RegisterRequest(
    val username: String,
    val email: String,
    val password: String,
    val firstName: String,
    val lastName: String,
    val phone: String?,
    val userType: String,
    // Rider profile fields (only for riders)
    val id_number: String? = null,
    val id_document: String? = null,
    val vehicle_type: String? = null,
    val vehicle_number: String? = null,
    val vehicle_document: String? = null,
    val emergency_contact: String? = null,
    val bank_account: String? = null,
    val bank_name: String? = null,
    val delivery_areas: List<String> = emptyList()
)
