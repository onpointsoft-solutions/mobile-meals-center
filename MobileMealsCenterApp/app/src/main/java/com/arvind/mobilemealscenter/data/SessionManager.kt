package com.arvind.mobilemealscenter.data

import android.content.Context
import android.content.SharedPreferences
import com.arvind.mobilemealscenter.model.User
import com.google.gson.Gson

class SessionManager(context: Context) {
    
    private val prefs: SharedPreferences = context.getSharedPreferences("MobileMealsCenterPrefs", Context.MODE_PRIVATE)
    private val gson = Gson()
    
    companion object {
        const val KEY_TOKEN = "auth_token"
        const val KEY_USER = "user_data"
        const val KEY_IS_LOGGED_IN = "is_logged_in"
        const val KEY_USER_TYPE = "user_type"
    }
    
    // Save authentication token
    fun saveAuthToken(token: String) {
        prefs.edit().putString(KEY_TOKEN, token).apply()
    }
    
    // Get authentication token
    fun getAuthToken(): String? {
        return prefs.getString(KEY_TOKEN, null)
    }
    
    // Save user data
    fun saveUser(user: User) {
        val userJson = gson.toJson(user)
        prefs.edit()
            .putString(KEY_USER, userJson)
            .putString(KEY_USER_TYPE, user.userType)
            .putBoolean(KEY_IS_LOGGED_IN, true)
            .apply()
    }
    
    // Get user data
    fun getUser(): User? {
        val userJson = prefs.getString(KEY_USER, null)
        return if (userJson != null) {
            gson.fromJson(userJson, User::class.java)
        } else {
            null
        }
    }
    
    // Check if user is logged in
    fun isLoggedIn(): Boolean {
        return prefs.getBoolean(KEY_IS_LOGGED_IN, false)
    }
    
    // Get user type
    fun getUserType(): String? {
        return prefs.getString(KEY_USER_TYPE, null)
    }
    
    // Check if user is rider
    fun isRider(): Boolean {
        return getUserType() == "rider"
    }
    
    // Check if user is customer
    fun isCustomer(): Boolean {
        return getUserType() == "customer"
    }
    
    // Check if rider is approved
    fun isRiderApproved(): Boolean {
        val user = getUser()
        return user?.let { 
            it.userType == "rider" && it.is_approved 
        } ?: false
    }
    
    // Get rider approval status
    fun getRiderApprovalStatus(): String? {
        val user = getUser()
        return if (user?.userType == "rider") {
            user.approval_status
        } else {
            null
        }
    }
    
    // Clear session (logout)
    fun clearSession() {
        prefs.edit()
            .remove(KEY_TOKEN)
            .remove(KEY_USER)
            .remove(KEY_IS_LOGGED_IN)
            .remove(KEY_USER_TYPE)
            .apply()
    }
    
    // Check if session is valid
    fun isSessionValid(): Boolean {
        return isLoggedIn() && getAuthToken() != null
    }
}
