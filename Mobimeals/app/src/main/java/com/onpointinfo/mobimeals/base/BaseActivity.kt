package com.onpointinfo.mobimeals.base

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.onpointinfo.mobimeals.auth.SessionManager
import kotlinx.coroutines.launch

abstract class BaseActivity : AppCompatActivity() {
    
    protected lateinit var sessionManager: SessionManager
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        sessionManager = SessionManager.getInstance(this)
        
        // Check authentication status
        if (!isLoginRequired() || sessionManager.isLoggedIn()) {
            setContentView(getLayoutResource())
            initializeViews()
            setupObservers()
            setupListeners()
        } else if (isLoginRequired()) {
            // Redirect to login if authentication is required
            redirectToLogin()
        }
    }
    
    protected abstract fun getLayoutResource(): Int
    protected abstract fun initializeViews()
    protected open fun setupObservers() {}
    protected open fun setupListeners() {}
    protected open fun isLoginRequired(): Boolean = true
    
    protected open fun redirectToLogin() {
        // Will be implemented in LoginActivity
        finish()
    }
    
    protected fun showToast(message: String, duration: Int = Toast.LENGTH_SHORT) {
        Toast.makeText(this, message, duration).show()
    }
    
    protected fun showLongToast(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show()
    }
    
    protected fun logoutUser() {
        lifecycleScope.launch {
            try {
                sessionManager.logout()
                redirectToLogin()
            } catch (e: Exception) {
                showToast("Error during logout: ${e.message}")
            }
        }
    }
    
    protected fun getCurrentUserId(): String? {
        return sessionManager.getCurrentUserId()
    }
    
    protected fun getCurrentUsername(): String? {
        return sessionManager.getCurrentUsername()
    }
    
    protected fun isCurrentUserCustomer(): Boolean {
        return sessionManager.isCustomer()
    }
    
    protected fun isCurrentUserRider(): Boolean {
        return sessionManager.isRider()
    }
    
    protected fun isCurrentUserRestaurant(): Boolean {
        return sessionManager.isRestaurant()
    }
}
