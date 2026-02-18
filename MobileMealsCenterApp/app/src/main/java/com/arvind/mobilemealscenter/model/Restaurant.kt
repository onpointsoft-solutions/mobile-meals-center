package com.arvind.mobilemealscenter.model

data class Restaurant(
    val id: Int,
    val name: String,
    val description: String,
    val address: String?,
    val phone: String?,
    val email: String?,
    val image: String?,
    val is_active: Boolean,
    val average_rating: Double,
    val delivery_fee: Double,
    val owner_name: String?
)

data class Meal(
    val id: Int,
    val name: String,
    val description: String,
    val price: Double,
    val image: String?,
    val restaurant: Int,
    val is_available: Boolean,
    val category: String?,
    val preparation_time: Int?
)

data class Category(
    val id: Int,
    val name: String,
    val description: String?,
    val image: String?
)
