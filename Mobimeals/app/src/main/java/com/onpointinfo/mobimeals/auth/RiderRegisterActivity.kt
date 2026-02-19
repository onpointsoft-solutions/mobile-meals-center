package com.onpointinfo.mobimeals.auth

import android.os.Bundle
import android.text.TextUtils
import android.view.View
import android.widget.ProgressBar
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.ViewModelProvider
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText
import com.onpointinfo.mobimeals.R
import com.onpointinfo.mobimeals.auth.LoginViewModel

class RiderRegisterActivity : AppCompatActivity() {
    
    private lateinit var authViewModel: LoginViewModel
    private lateinit var progressBar: ProgressBar
    
    // UI Components
    private lateinit var etFirstName: TextInputEditText
    private lateinit var etLastName: TextInputEditText
    private lateinit var etUsername: TextInputEditText
    private lateinit var etEmail: TextInputEditText
    private lateinit var etPhone: TextInputEditText
    private lateinit var etPassword: TextInputEditText
    private lateinit var etConfirmPassword: TextInputEditText
    private lateinit var btnRegister: MaterialButton
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_rider_register)
        
        // Initialize ViewModel
        authViewModel = ViewModelProvider(this)[LoginViewModel::class.java]
        
        // Initialize UI components
        initViews()
        setupClickListeners()
        setupObservers()
    }
    
    private fun initViews() {
        // Form fields
        etFirstName = findViewById(R.id.etFirstName)
        etLastName = findViewById(R.id.etLastName)
        etUsername = findViewById(R.id.etUsername)
        etEmail = findViewById(R.id.etEmail)
        etPhone = findViewById(R.id.etPhone)
        etPassword = findViewById(R.id.etPassword)
        etConfirmPassword = findViewById(R.id.etConfirmPassword)
        
        // Buttons
        btnRegister = findViewById(R.id.btnRegister)
        
        // Progress bar
        progressBar = findViewById(R.id.progressBar)
        
        // Back button
        findViewById<View>(R.id.btnBack).setOnClickListener {
            finish()
        }
        
        // Login link
        findViewById<View>(R.id.tvLoginLink).setOnClickListener {
            finish() // Go back to login
        }
    }
    
    private fun setupClickListeners() {
        btnRegister.setOnClickListener {
            if (validateForm()) {
                registerRider()
            }
        }
    }
    
    private fun setupObservers() {
        authViewModel.registrationResult.observe(this) { result ->
            progressBar.visibility = View.GONE
            
            result.onSuccess { loginResponse ->
                Toast.makeText(
                    this,
                    loginResponse.message,
                    Toast.LENGTH_LONG
                ).show()
                
                // Navigate back to login
                finish()
            }
            
            result.onFailure { exception ->
                Toast.makeText(
                    this,
                    "Registration failed: ${exception.message}",
                    Toast.LENGTH_LONG
                ).show()
            }
        }
    }
    
    private fun validateForm(): Boolean {
        val firstName = etFirstName.text.toString().trim()
        val lastName = etLastName.text.toString().trim()
        val username = etUsername.text.toString().trim()
        val email = etEmail.text.toString().trim()
        val phone = etPhone.text.toString().trim()
        val password = etPassword.text.toString()
        val confirmPassword = etConfirmPassword.text.toString()
        
        // Validate required fields
        if (TextUtils.isEmpty(firstName)) {
            etFirstName.error = "First name is required"
            etFirstName.requestFocus()
            return false
        }
        
        if (TextUtils.isEmpty(lastName)) {
            etLastName.error = "Last name is required"
            etLastName.requestFocus()
            return false
        }
        
        if (TextUtils.isEmpty(username)) {
            etUsername.error = "Username is required"
            etUsername.requestFocus()
            return false
        }
        
        if (username.length < 3) {
            etUsername.error = "Username must be at least 3 characters"
            etUsername.requestFocus()
            return false
        }
        
        if (TextUtils.isEmpty(email)) {
            etEmail.error = "Email is required"
            etEmail.requestFocus()
            return false
        }
        
        if (!android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
            etEmail.error = "Please enter a valid email"
            etEmail.requestFocus()
            return false
        }
        
        if (TextUtils.isEmpty(password)) {
            etPassword.error = "Password is required"
            etPassword.requestFocus()
            return false
        }
        
        if (password.length < 6) {
            etPassword.error = "Password must be at least 6 characters"
            etPassword.requestFocus()
            return false
        }
        
        if (password != confirmPassword) {
            etConfirmPassword.error = "Passwords do not match"
            etConfirmPassword.requestFocus()
            return false
        }
        
        return true
    }
    
    private fun registerRider() {
        progressBar.visibility = View.VISIBLE
        
        val firstName = etFirstName.text.toString().trim()
        val lastName = etLastName.text.toString().trim()
        val username = etUsername.text.toString().trim()
        val email = etEmail.text.toString().trim()
        val phone = etPhone.text.toString().trim()
        val password = etPassword.text.toString()
        
        authViewModel.registerRider(
            username = username,
            email = email,
            password = password,
            firstName = firstName,
            lastName = lastName,
            phone = phone
        )
    }
}
