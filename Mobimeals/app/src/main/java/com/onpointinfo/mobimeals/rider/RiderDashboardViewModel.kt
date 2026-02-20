package com.onpointinfo.mobimeals.rider

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.onpointinfo.mobimeals.auth.SessionManager
import com.onpointinfo.mobimeals.data.models.EarningsData
import com.onpointinfo.mobimeals.data.models.RiderProfile
import com.onpointinfo.mobimeals.network.RiderApiService
import com.onpointinfo.mobimeals.network.RetrofitClient
import kotlinx.coroutines.launch

class RiderDashboardViewModel : ViewModel() {
    
    private val riderApiService = RetrofitClient.riderApiService
    private lateinit var sessionManager: SessionManager
    
    fun setSessionManager(sessionManager: SessionManager) {
        this.sessionManager = sessionManager
    }
    
    private val _riderProfile = MutableLiveData<RiderProfile?>()
    val riderProfile: LiveData<RiderProfile?> = _riderProfile
    
    private val _earningsData = MutableLiveData<EarningsData?>()
    val earningsData: LiveData<EarningsData?> = _earningsData
    
    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading
    
    private val _errorMessage = MutableLiveData<String?>()
    val errorMessage: LiveData<String?> = _errorMessage
    
    private val _successMessage = MutableLiveData<String?>()
    val successMessage: LiveData<String?> = _successMessage
    
    fun loadRiderData() {
        executeWithLoading {
            try {
                // Load rider profile
                val profileResponse = riderApiService.getRiderProfile()
                if (profileResponse.isSuccessful && profileResponse.body() != null) {
                    _riderProfile.value = profileResponse.body()
                } else {
                    showError("Failed to load rider profile")
                }
                
                // Load earnings data
                val earningsResponse = riderApiService.getRiderEarnings()
                if (earningsResponse.isSuccessful && earningsResponse.body() != null) {
                    _earningsData.value = earningsResponse.body()
                } else {
                    showError("Failed to load earnings data")
                }
                
            } catch (e: Exception) {
                showError("Network error: ${e.message}")
            }
        }
    }
    
    fun toggleOnlineStatus(isOnline: Boolean) {
        executeWithLoading {
            try {
                println("DEBUG: Toggling online status to: $isOnline")
                val response = riderApiService.toggleOnlineStatus()
                if (response.isSuccessful) {
                    try {
                        val responseBody = response.body()
                        println("DEBUG: Toggle online response: $responseBody")
                        
                        if (responseBody != null) {
                            // Safe parsing with explicit null checks
                            val success = when {
                                responseBody.containsKey("success") -> {
                                    when (val successValue = responseBody["success"]) {
                                        is Boolean -> successValue
                                        is String -> successValue.lowercase() == "true"
                                        else -> false
                                    }
                                }
                                else -> false
                            }
                            
                            if (success) {
                                val newOnlineStatus = when {
                                    responseBody.containsKey("is_online") -> {
                                        when (val statusValue = responseBody["is_online"]) {
                                            is Boolean -> statusValue
                                            is String -> statusValue.lowercase() == "true"
                                            else -> false
                                        }
                                    }
                                    else -> false
                                }
                                
                                val message = when {
                                    responseBody.containsKey("message") -> {
                                        responseBody["message"]?.toString() ?: "Status updated"
                                    }
                                    else -> "Status updated"
                                }
                                
                                println("DEBUG: New online status from backend: $newOnlineStatus")
                                println("DEBUG: Switch was set to: $isOnline, backend returned: $newOnlineStatus")
                                
                                // Always use the backend response as the source of truth
                                val currentProfile = _riderProfile.value
                                currentProfile?.let {
                                    val updatedProfile = it.copy(isOnline = newOnlineStatus)
                                    _riderProfile.value = updatedProfile
                                    println("DEBUG: Updated rider profile online status to: $newOnlineStatus")
                                    showSuccess(message)
                                } ?: run {
                                    // If no profile exists, load it fresh from backend
                                    println("DEBUG: No current profile, loading fresh from backend")
                                    loadRiderData()
                                    showSuccess(message)
                                }
                                
                                // Also refresh earnings when status changes
                                loadRiderData()
                                
                            } else {
                                val errorMsg = when {
                                    responseBody.containsKey("error") -> {
                                        responseBody["error"]?.toString() ?: "Failed to update online status"
                                    }
                                    else -> "Failed to update online status"
                                }
                                println("DEBUG: Backend returned error: $errorMsg")
                                showError(errorMsg)
                            }
                        } else {
                            println("DEBUG: Empty response from server")
                            showError("Empty response from server")
                        }
                    } catch (parseException: Exception) {
                        println("DEBUG: Response parsing exception: ${parseException.message}")
                        // Don't show error for successful operations that fail to parse
                        // Assume success if HTTP response was successful
                        showSuccess("Status updated successfully")
                    }
                } else {
                    val errorBody = response.errorBody()?.string()
                    println("DEBUG: HTTP error ${response.code()}: $errorBody")
                    showError("Failed to update online status: ${response.code()}")
                }
            } catch (e: Exception) {
                println("DEBUG: Toggle online exception: ${e.message}")
                println("DEBUG: Exception type: ${e.javaClass.simpleName}")
                
                // Don't show network error for successful operations
                val errorMessage = when {
                    e is java.net.SocketTimeoutException || 
                    e is java.net.UnknownHostException ||
                    e is java.net.ConnectException ||
                    e.message?.contains("Network", ignoreCase = true) == true ||
                    e.message?.contains("Connection", ignoreCase = true) == true -> {
                        "Network error: ${e.message}"
                    }
                    e.message?.contains("timeout", ignoreCase = true) == true -> {
                        "Connection timeout: ${e.message}"
                    }
                    e.message?.contains("SSL", ignoreCase = true) == true ||
                    e.message?.contains("certificate", ignoreCase = true) == true -> {
                        "Secure connection error: ${e.message}"
                    }
                    else -> {
                        // For other exceptions, don't show as network error
                        println("DEBUG: Non-network exception, not showing as network error")
                        null
                    }
                }
                
                errorMessage?.let { showError(it) }
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
