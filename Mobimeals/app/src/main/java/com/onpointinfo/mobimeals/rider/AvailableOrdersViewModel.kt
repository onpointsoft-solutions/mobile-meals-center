package com.onpointinfo.mobimeals.rider

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.onpointinfo.mobimeals.data.models.Order
import com.onpointinfo.mobimeals.network.RetrofitClient
import kotlinx.coroutines.launch

class AvailableOrdersViewModel : ViewModel() {
    
    private val riderApiService = RetrofitClient.riderApiService
    
    private val _availableOrders = MutableLiveData<List<Order>>()
    val availableOrders: LiveData<List<Order>> = _availableOrders
    
    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading
    
    private val _errorMessage = MutableLiveData<String?>()
    val errorMessage: LiveData<String?> = _errorMessage
    
    private val _successMessage = MutableLiveData<String?>()
    val successMessage: LiveData<String?> = _successMessage
    
    fun loadAvailableOrders() {
        executeWithLoading {
            try {
                val response = riderApiService.getAvailableOrders()
                if (response.isSuccessful && response.body() != null) {
                    // Handle the response properly - it might be a list of orders or a different structure
                    val responseBody = response.body()
                    if (responseBody is List<*>) {
                        // Convert to proper Order objects if possible
                        val orders = responseBody.filterIsInstance<Order>()
                        _availableOrders.value = orders
                        
                        if (orders.isEmpty()) {
                            showSuccess("No orders available for delivery at the moment")
                        }
                    } else {
                        _availableOrders.value = emptyList()
                        showSuccess("No orders available for delivery at the moment")
                    }
                } else {
                    // Handle specific HTTP errors
                    val errorMessage = when (response.code()) {
                        403 -> "You must be online to view available orders. Please toggle your online status."
                        401 -> "Authentication required. Please login again."
                        404 -> "No orders found."
                        500 -> "Server error. Please try again later."
                        else -> "Failed to load available orders. Please try again."
                    }
                    showError(errorMessage)
                    _availableOrders.value = emptyList()
                }
            } catch (e: Exception) {
                // Provide user-friendly error messages
                val errorMessage = when {
                    e is java.net.SocketTimeoutException || 
                    e is java.net.UnknownHostException ||
                    e is java.net.ConnectException ||
                    e.message?.contains("Network", ignoreCase = true) == true ||
                    e.message?.contains("Connection", ignoreCase = true) == true -> {
                        "No internet connection. Please check your network and try again."
                    }
                    e.message?.contains("timeout", ignoreCase = true) == true -> {
                        "Connection timeout. Please check your internet connection and try again."
                    }
                    else -> {
                        "Network error occurred. Please check your internet connection and try again."
                    }
                }
                showError(errorMessage)
                _availableOrders.value = emptyList()
            }
        }
    }
    
    fun acceptOrder(orderId: String) {
        executeWithLoading {
            try {
                val response = riderApiService.acceptOrder(orderId)
                if (response.isSuccessful) {
                    showSuccess("Order accepted successfully!")
                    // Refresh the list
                    loadAvailableOrders()
                } else {
                    showError("Failed to accept order")
                }
            } catch (e: Exception) {
                showError("Network error: ${e.message}")
            }
        }
    }
    
    private fun setLoading(loading: Boolean) {
        _isLoading.value = loading
    }
    
    protected fun showError(message: String) {
        _errorMessage.value = message
    }
    
    protected fun showSuccess(message: String) {
        _successMessage.value = message
    }
    
    fun clearError() {
        _errorMessage.value = null
    }
    
    fun clearSuccess() {
        _successMessage.value = null
    }
    
    private fun executeWithLoading(
        action: suspend () -> Unit
    ) {
        viewModelScope.launch {
            try {
                setLoading(true)
                action()
            } catch (e: Exception) {
                showError(e.message ?: "An error occurred")
            } finally {
                setLoading(false)
            }
        }
    }
}
