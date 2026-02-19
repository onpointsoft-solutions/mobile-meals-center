package com.onpointinfo.mobimeals.rider

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.onpointinfo.mobimeals.data.models.Order
import com.onpointinfo.mobimeals.network.RiderApiService
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
                    _availableOrders.value = response.body()!!
                } else {
                    showError("Failed to load available orders")
                }
            } catch (e: Exception) {
                showError("Network error: ${e.message}")
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
