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
                val errorMessage = response.errorBody()?.string() ?: "Login failed with code ${response.code()}"
                println("DEBUG: Login failed - HTTP ${response.code()}: $errorMessage")
                Result.failure(Exception(errorMessage))
            }
        } catch (e: Exception) {
            println("DEBUG: Login exception: ${e.message}")
            Result.failure(e)
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
