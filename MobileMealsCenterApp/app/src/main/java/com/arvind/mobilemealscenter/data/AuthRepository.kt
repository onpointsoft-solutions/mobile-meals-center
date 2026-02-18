package com.arvind.mobilemealscenter.data

import com.arvind.mobilemealscenter.model.LoginRequest
import com.arvind.mobilemealscenter.model.LoginResponse
import com.arvind.mobilemealscenter.model.RegisterRequest
import com.arvind.mobilemealscenter.model.User
import retrofit2.Response

class AuthRepository(
    private val apiService: ApiService,
    private val sessionManager: SessionManager
) {
    
    suspend fun login(username: String, password: String): Result<LoginResponse> {
        return try {
            val loginRequest = LoginRequest(username, password)
            val response = apiService.login(loginRequest)
            
            if (response.isSuccessful) {
                val loginResponse = response.body()
                if (loginResponse != null) {
                    // Save token and user data
                    sessionManager.saveAuthToken(loginResponse.token)
                    sessionManager.saveUser(loginResponse.user)
                    Result.success(loginResponse)
                } else {
                    Result.failure(Exception("Invalid response from server"))
                }
            } else {
                val errorMessage = response.errorBody()?.string() ?: "Login failed"
                Result.failure(Exception(errorMessage))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun register(registerRequest: RegisterRequest): Result<User> {
        return try {
            val response = apiService.register(registerRequest)
            
            if (response.isSuccessful) {
                val user = response.body()
                if (user != null) {
                    Result.success(user)
                } else {
                    Result.failure(Exception("Invalid response from server"))
                }
            } else {
                val errorMessage = response.errorBody()?.string() ?: "Registration failed"
                Result.failure(Exception(errorMessage))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getCurrentUser(): Result<User> {
        return try {
            val token = sessionManager.getAuthToken()
            if (token != null) {
                val response = apiService.getCurrentUser("Bearer $token")
                if (response.isSuccessful) {
                    val user = response.body()
                    if (user != null) {
                        sessionManager.saveUser(user)
                        Result.success(user)
                    } else {
                        Result.failure(Exception("Invalid response from server"))
                    }
                } else {
                    Result.failure(Exception("Failed to get user data"))
                }
            } else {
                Result.failure(Exception("No authentication token found"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    fun logout() {
        sessionManager.clearSession()
    }
    
    fun isLoggedIn(): Boolean {
        return sessionManager.isLoggedIn()
    }
    
    fun getUserType(): String? {
        return sessionManager.getUserType()
    }
    
    fun isRider(): Boolean {
        return sessionManager.isRider()
    }
    
    fun isCustomer(): Boolean {
        return sessionManager.isCustomer()
    }
    
    fun isRiderApproved(): Boolean {
        return sessionManager.isRiderApproved()
    }
    
    fun getRiderApprovalStatus(): String? {
        return sessionManager.getRiderApprovalStatus()
    }
    
    fun getAuthToken(): String? {
        return sessionManager.getAuthToken()
    }
}
