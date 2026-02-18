package com.arvind.mobilemealscenter.model

data class Order(
    val id: Int,
    val order_number: String,
    val customer: User,
    val restaurant: Restaurant,
    val status: String, // "pending", "confirmed", "preparing", "ready", "delivering", "delivered", "cancelled"
    val total_amount: Double,
    val delivery_address: String,
    val phone: String,
    val special_instructions: String?,
    val created_at: String,
    val updated_at: String,
    val delivery_time: String?,
    val items: List<OrderItem>
)

data class OrderItem(
    val id: Int,
    val order: Int,
    val meal: Meal,
    val quantity: Int,
    val price: Double,
    val total_price: Double,
    val notes: String?
)

data class OrderStatus(
    val status: String,
    val display_name: String,
    val color: String,
    val timestamp: String?
)

// For rider-specific data
data class DeliveryAssignment(
    val id: Int,
    val order: Order,
    val rider: User,
    val status: String, // "assigned", "picked_up", "delivering", "delivered"
    val assigned_at: String,
    val picked_up_at: String?,
    val delivered_at: String?,
    val delivery_notes: String?
)
