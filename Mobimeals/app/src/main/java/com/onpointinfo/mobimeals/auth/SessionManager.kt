package com.onpointinfo.mobimeals.auth

import android.content.Context
import android.content.SharedPreferences
import com.onpointinfo.mobimeals.data.models.User
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class SessionManager private constructor(private val context: Context) {
    
    private val sharedPreferences: SharedPreferences = 
        context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
    
    companion object {
        private const val PREF_NAME = "mobimeals_session"
        private const val KEY_IS_LOGGED_IN = "is_logged_in"
        private const val KEY_USER_ID = "user_id"
        private const val KEY_USERNAME = "username"
        private const val KEY_EMAIL = "email"
        private const val KEY_USER_TYPE = "user_type"
        private const val KEY_ACCESS_TOKEN = "access_token"
        private const val KEY_REFRESH_TOKEN = "refresh_token"
        
        @Volatile
        private var INSTANCE: SessionManager? = null
        
        fun getInstance(context: Context): SessionManager {
            return INSTANCE ?: synchronized(this) {
                INSTANCE ?: SessionManager(context).also { INSTANCE = it }
            }
        }
    }
    
    suspend fun saveLoginSession(
        user: User,
        accessToken: String,
        refreshToken: String
    ) {
        // Save to SharedPreferences only
        sharedPreferences.edit().apply {
            putBoolean(KEY_IS_LOGGED_IN, true)
            putString(KEY_USER_ID, user.id)
            putString(KEY_USERNAME, user.username)
            putString(KEY_EMAIL, user.email)
            putString(KEY_USER_TYPE, user.userType)
            putString(KEY_ACCESS_TOKEN, accessToken)
            putString(KEY_REFRESH_TOKEN, refreshToken)
            apply()
        }
    }
    
    suspend fun logout() {
        // Clear SharedPreferences only
        sharedPreferences.edit().clear().apply()
    }
    
    fun isLoggedIn(): Boolean {
        return sharedPreferences.getBoolean(KEY_IS_LOGGED_IN, false)
    }
    
    fun getCurrentUserId(): String? {
        return sharedPreferences.getString(KEY_USER_ID, null)
    }
    
    fun getCurrentUsername(): String? {
        return sharedPreferences.getString(KEY_USERNAME, null)
    }
    
    fun getCurrentEmail(): String? {
        return sharedPreferences.getString(KEY_EMAIL, null)
    }
    
    fun getCurrentUserType(): String? {
        return sharedPreferences.getString(KEY_USER_TYPE, null)
    }
    
    fun getAccessToken(): String? {
        return sharedPreferences.getString(KEY_ACCESS_TOKEN, null)
    }
    
    fun getRefreshToken(): String? {
        return sharedPreferences.getString(KEY_REFRESH_TOKEN, null)
    }
    
    fun isCustomer(): Boolean {
        return getCurrentUserType() == "customer"
    }
    
    fun isRider(): Boolean {
        return getCurrentUserType() == "rider"
    }
    
    fun isRestaurant(): Boolean {
        return getCurrentUserType() == "restaurant"
    }
    
    fun updateTokens(accessToken: String, refreshToken: String) {
        sharedPreferences.edit().apply {
            putString(KEY_ACCESS_TOKEN, accessToken)
            putString(KEY_REFRESH_TOKEN, refreshToken)
            apply()
        }
    }
}
