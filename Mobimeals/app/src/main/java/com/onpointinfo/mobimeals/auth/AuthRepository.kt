package com.onpointinfo.mobimeals.auth

import com.onpointinfo.mobimeals.network.RetrofitClient
import com.onpointinfo.mobimeals.data.models.User
import com.onpointinfo.mobimeals.network.LoginRequest
import com.onpointinfo.mobimeals.network.LoginResponse
import com.onpointinfo.mobimeals.network.RiderRegistrationRequest
import retrofit2.Response
import java.util.regex.Pattern

class AuthRepository private constructor() {
    
    private val authApiService = RetrofitClient.authApiService
    
    companion object {
        @Volatile
        private var INSTANCE: AuthRepository? = null
        
        fun getInstance(): AuthRepository {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: AuthRepository().also { INSTANCE = it }
            }
        }
    }
    
    suspend fun login(username: String, password: String, userType: String): Result<LoginResponse> {
        return try {
            println("DEBUG: Attempting rider API login for user: $username")
            
            // Create login request for rider API
            val loginRequest = LoginRequest(username, password)
            val response = authApiService.login(loginRequest)
            
            println("DEBUG: Login response code: ${response.code()}")
            
            if (response.isSuccessful && response.body() != null) {
                val loginResponse = response.body()!!
                println("DEBUG: Login response success: ${loginResponse.success}")
                
                if (loginResponse.success) {
                    println("DEBUG: Login successful - token: ${loginResponse.access_token}")
                    Result.success(loginResponse)
                } else {
                    println("DEBUG: Login failed: ${loginResponse.message}")
                    Result.failure(Exception(loginResponse.message))
                }
            } else {
                val rawErrorMessage = response.errorBody()?.string() ?: "Login failed with code ${response.code()}"
                println("DEBUG: Login failed - HTTP ${response.code()}: $rawErrorMessage")
                
                // Provide user-friendly error messages based on response code and content
                val userMessage = when {
                    response.code() == 403 && rawErrorMessage.contains("not approved", ignoreCase = true) -> {
                        "Your account is pending approval. Please wait for admin approval or contact support."
                    }
                    response.code() == 403 && rawErrorMessage.contains("suspended", ignoreCase = true) -> {
                        "Your account has been suspended. Please contact support for assistance."
                    }
                    response.code() == 403 && rawErrorMessage.contains("not a rider", ignoreCase = true) -> {
                        "This account is not registered as a rider. Please register as a rider first."
                    }
                    response.code() == 401 -> {
                        "Invalid username or password. Please check your credentials and try again."
                    }
                    response.code() == 400 -> {
                        "Invalid login information. Please check your username and password."
                    }
                    response.code() == 500 -> {
                        "Server error occurred. Please try again later or contact support."
                    }
                    response.code() == 502 || response.code() == 503 -> {
                        "Service temporarily unavailable. Please try again in a few minutes."
                    }
                    rawErrorMessage.contains("approval", ignoreCase = true) -> {
                        "Your account is pending approval. Please wait for admin approval."
                    }
                    rawErrorMessage.contains("suspended", ignoreCase = true) -> {
                        "Your account has been suspended. Please contact support."
                    }
                    rawErrorMessage.contains("invalid", ignoreCase = true) -> {
                        "Invalid username or password. Please check your credentials."
                    }
                    else -> {
                        "Login failed. Please check your credentials and try again."
                    }
                }
                
                Result.failure(Exception(userMessage))
            }
        } catch (e: Exception) {
            println("DEBUG: Login exception: ${e.message}")
            
            // Provide user-friendly error messages
            val userMessage = when {
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
                e.message?.contains("SSL", ignoreCase = true) == true ||
                e.message?.contains("certificate", ignoreCase = true) == true -> {
                    "Secure connection failed. Please try again later."
                }
                else -> {
                    "Network error occurred. Please check your internet connection and try again."
                }
            }
            
            Result.failure(Exception(userMessage))
        }
    }
    
    suspend fun registerRider(
        username: String,
        email: String,
        password: String,
        firstName: String,
        lastName: String,
        phone: String = ""
    ): Result<LoginResponse> {
        return try {
            println("DEBUG: Attempting rider registration for user: $username")
            
            // Create registration request
            val registrationRequest = RiderRegistrationRequest(
                username = username,
                email = email,
                password = password,
                first_name = firstName,
                last_name = lastName,
                phone = phone
            )
            
            val response = authApiService.register(registrationRequest)
            println("DEBUG: Registration response code: ${response.code()}")
            
            if (response.isSuccessful && response.body() != null) {
                val registrationResponse = response.body()!!
                println("DEBUG: Registration response success: ${registrationResponse.success}")
                
                if (registrationResponse.success) {
                    println("DEBUG: Registration successful - approval status: ${registrationResponse.user?.isApproved}")
                    Result.success(registrationResponse)
                } else {
                    println("DEBUG: Registration failed: ${registrationResponse.message}")
                    Result.failure(Exception(registrationResponse.message))
                }
            } else {
                val errorMessage = response.errorBody()?.string() ?: "Registration failed with code ${response.code()}"
                println("DEBUG: Registration failed - HTTP ${response.code()}: $errorMessage")
                Result.failure(Exception(errorMessage))
            }
        } catch (e: Exception) {
            println("DEBUG: Registration exception: ${e.message}")
            Result.failure(e)
        }
    }
    
        
    suspend fun logout(): Result<Boolean> {
        return try {
            val response = authApiService.logout()
            if (response.isSuccessful) {
                Result.success(true)
            } else {
                Result.failure(Exception("Logout failed"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun refreshToken(refreshToken: String): Result<LoginResponse> {
        return try {
            val response = authApiService.refreshToken(
                com.onpointinfo.mobimeals.network.RefreshTokenRequest(refreshToken)
            )
            
            if (response.isSuccessful && response.body() != null) {
                val loginResponse = response.body()!!
                if (loginResponse.success && loginResponse.access_token != null) {
                    Result.success(loginResponse)
                } else {
                    Result.failure(Exception(loginResponse.message))
                }
            } else {
                val errorMessage = response.errorBody()?.string() ?: "Token refresh failed"
                Result.failure(Exception(errorMessage))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getCurrentUser(): Result<User> {
        return try {
            val response = authApiService.getCurrentUser()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val errorMessage = response.errorBody()?.string() ?: "Failed to get user info"
                Result.failure(Exception(errorMessage))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
