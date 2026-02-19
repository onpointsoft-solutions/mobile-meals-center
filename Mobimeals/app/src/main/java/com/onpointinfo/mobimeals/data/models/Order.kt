package com.onpointinfo.mobimeals.data.models

import com.google.gson.annotations.SerializedName

data class Order(
    @SerializedName("id")
    val id: String,
    
    @SerializedName("customer")
    val customer: Customer,
    
    @SerializedName("restaurant")
    val restaurant: Restaurant,
    
    @SerializedName("status")
    val status: String,
    
    @SerializedName("total_amount")
    val totalAmount: Double,
    
    @SerializedName("delivery_address")
    val deliveryAddress: String,
    
    @SerializedName("phone")
    val phone: String,
    
    @SerializedName("notes")
    val notes: String = "",
    
    @SerializedName("created_at")
    val createdAt: String,
    
    @SerializedName("updated_at")
    val updatedAt: String,
    
    @SerializedName("order_number")
    val orderNumber: String = "",

    @SerializedName("estimated_delivery_time")
    val estimatedDeliveryTime: String = ""
)

data class Customer(
    @SerializedName("id")
    val id: String,
    
    @SerializedName("username")
    val username: String,
    
    @SerializedName("first_name")
    val firstName: String = "",
    
    @SerializedName("last_name")
    val lastName: String = "",
    
    @SerializedName("email")
    val email: String = ""
)

data class Restaurant(
    @SerializedName("id")
    val id: String,
    
    @SerializedName("name")
    val name: String,
    
    @SerializedName("description")
    val description: String,
    
    @SerializedName("phone")
    val phone: String,
    
    @SerializedName("address")
    val address: String,
    
    @SerializedName("logo")
    val logo: String? = null,
    
    @SerializedName("latitude")
    val latitude: Double? = null,
    
    @SerializedName("longitude")
    val longitude: Double? = null,
    
    @SerializedName("is_active")
    val isActive: Boolean = true,
    
    @SerializedName("rating")
    val rating: Float = 0.0f
)

data class OrderItem(
    @SerializedName("id")
    val id: String,
    
    @SerializedName("meal")
    val meal: Meal,
    
    @SerializedName("quantity")
    val quantity: Int,
    
    @SerializedName("price")
    val price: Double
)

data class Meal(
    @SerializedName("id")
    val id: String,
    
    @SerializedName("name")
    val name: String,
    
    @SerializedName("description")
    val description: String = "",
    
    @SerializedName("price")
    val price: Double,
    
    @SerializedName("image")
    val image: String? = null,
    
    @SerializedName("category")
    val category: String = ""
)
