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
                val response = riderApiService.toggleOnlineStatus()
                if (response.isSuccessful) {
                    val responseBody = response.body()
                    if (responseBody != null && responseBody["success"] == true) {
                        val currentProfile = _riderProfile.value
                        currentProfile?.let {
                            val newOnlineStatus = responseBody["is_online"] as Boolean
                            _riderProfile.value = it.copy(isOnline = newOnlineStatus)
                            val message = responseBody["message"] as String
                            showSuccess(message)
                        }
                    } else {
                        showError("Failed to update online status")
                    }
                } else {
                    showError("Failed to update online status")
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
