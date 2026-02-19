package com.onpointinfo.mobimeals.auth

import android.content.Intent
import android.os.Bundle
import android.widget.*
import androidx.lifecycle.ViewModelProvider
import com.onpointinfo.mobimeals.MainActivity
import com.onpointinfo.mobimeals.R
import com.onpointinfo.mobimeals.base.BaseActivity
import com.onpointinfo.mobimeals.rider.RiderDashboardActivity
import kotlin.jvm.java

class LoginActivity : BaseActivity() {
    
    private lateinit var loginViewModel: LoginViewModel
    private lateinit var etUsername: EditText
    private lateinit var etPassword: EditText
    private lateinit var rgUserType: RadioGroup
    private lateinit var rbCustomer: RadioButton
    private lateinit var rbRider: RadioButton
    private lateinit var btnLogin: Button
    private lateinit var progressBar: ProgressBar
    
    override fun isLoginRequired(): Boolean = false
    
    override fun getLayoutResource(): Int = R.layout.activity_login
    
    override fun initializeViews() {
        etUsername = findViewById(R.id.etUsername)
        etPassword = findViewById(R.id.etPassword)
        rgUserType = findViewById(R.id.rgUserType)
        rbCustomer = findViewById(R.id.rbCustomer)
        rbRider = findViewById(R.id.rbRider)
        btnLogin = findViewById(R.id.btnLogin)
        progressBar = findViewById(R.id.progressBar)
        
        loginViewModel = ViewModelProvider(this)[LoginViewModel::class.java]
    }
    
    override fun setupObservers() {
        loginViewModel.isLoading.observe(this) { isLoading ->
            progressBar.visibility = if (isLoading) android.view.View.VISIBLE else android.view.View.GONE
            btnLogin.isEnabled = !isLoading
        }
        
        loginViewModel.errorMessage.observe(this) { errorMessage ->
            errorMessage?.let {
                showToast(it)
                loginViewModel.clearError()
            }
        }
        
        loginViewModel.successMessage.observe(this) { successMessage ->
            successMessage?.let {
                showToast(it)
                loginViewModel.clearSuccess()
            }
        }
        
        loginViewModel.loginSuccess.observe(this) { isSuccess ->
            if (isSuccess) {
                navigateToDashboard()
            }
        }
    }
    
    override fun setupListeners() {
        btnLogin.setOnClickListener {
            performLogin()
        }
        
        rgUserType.setOnCheckedChangeListener { _, checkedId ->
            when (checkedId) {
                R.id.rbCustomer -> {
                    etUsername.hint = "Customer Email"
                }
                R.id.rbRider -> {
                    etUsername.hint = "Rider Username"
                }
            }
        }
    }
    
    private fun performLogin() {
        val username = etUsername.text.toString().trim()
        val password = etPassword.text.toString().trim()
        val userType = when (rgUserType.checkedRadioButtonId) {
            R.id.rbCustomer -> "customer"
            R.id.rbRider -> "rider"
            else -> ""
        }
        
        if (username.isEmpty()) {
            showToast("Please enter username/email")
            return
        }
        
        if (password.isEmpty()) {
            showToast("Please enter password")
            return
        }
        
        if (userType.isEmpty()) {
            showToast("Please select user type")
            return
        }
        
        loginViewModel.login(username, password, userType)
    }
    
    private fun navigateToDashboard() {
        val intent = when (sessionManager.getCurrentUserType()) {
            "customer" -> Intent(this, MainActivity::class.java)
            "rider" -> Intent(this, RiderDashboardActivity::class.java)
            else -> null
        }
        
        intent?.let {
            startActivity(it)
            finish()
        }
    }
    
    override fun redirectToLogin() {
        // Already at login screen, no action needed
    }
}
