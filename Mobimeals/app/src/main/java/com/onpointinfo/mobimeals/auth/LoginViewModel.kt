package com.onpointinfo.mobimeals.auth

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.onpointinfo.mobimeals.network.LoginResponse
import kotlinx.coroutines.launch

class LoginViewModel : ViewModel() {
    
    private val authRepository = AuthRepository.getInstance()
    
    private val _loginSuccess = MutableLiveData<Boolean>()
    val loginSuccess: LiveData<Boolean> = _loginSuccess
    
    private val _registrationResult = MutableLiveData<Result<LoginResponse>>()
    val registrationResult: LiveData<Result<LoginResponse>> = _registrationResult
    
    fun login(username: String, password: String, userType: String) {
        executeWithLoading {
            val result = authRepository.login(username, password, userType)
            
            result.fold(
                onSuccess = { loginResponse ->
                    // Session will be saved in the Activity
                    _loginSuccess.value = true
                    showSuccess("Login successful!")
                },
                onFailure = { exception ->
                    showError(exception.message ?: "Login failed")
                }
            )
        }
    }
    
    fun registerRider(
        username: String,
        email: String,
        password: String,
        firstName: String,
        lastName: String,
        phone: String = ""
    ) {
        executeWithLoading {
            val result = authRepository.registerRider(
                username, email, password, firstName, lastName, phone
            )
            
            _registrationResult.value = result
        }
    }
    
    // Import from BaseViewModel
    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading
    
    private val _errorMessage = MutableLiveData<String?>()
    val errorMessage: LiveData<String?> = _errorMessage
    
    private val _successMessage = MutableLiveData<String?>()
    val successMessage: LiveData<String?> = _successMessage
    
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
