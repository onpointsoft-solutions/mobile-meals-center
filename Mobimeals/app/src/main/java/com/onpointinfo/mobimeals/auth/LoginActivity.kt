package com.onpointinfo.mobimeals.auth

import android.animation.Animator
import android.animation.AnimatorSet
import android.animation.ObjectAnimator
import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import android.view.animation.AccelerateDecelerateInterpolator
import android.view.animation.OvershootInterpolator
import android.widget.*
import androidx.core.view.ViewCompat
import androidx.core.view.ViewPropertyAnimatorCompat
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.lifecycleScope
import com.onpointinfo.mobimeals.MainActivity
import com.onpointinfo.mobimeals.R
import com.onpointinfo.mobimeals.base.BaseActivity
import com.onpointinfo.mobimeals.rider.RiderDashboardActivity
import kotlinx.coroutines.launch

class LoginActivity : BaseActivity() {
    
    private lateinit var loginViewModel: LoginViewModel
    private lateinit var etUsername: EditText
    private lateinit var etPassword: EditText
    private lateinit var rgUserType: RadioGroup
    private lateinit var rbCustomer: RadioButton
    private lateinit var rbRider: RadioButton
    private lateinit var btnLogin: Button
    private lateinit var tvRegisterRider: TextView
    private lateinit var progressBar: ProgressBar
    private lateinit var ivLogo: View
    private lateinit var tvTitle: TextView
    private lateinit var tvSubtitle: TextView
    
    override fun isLoginRequired(): Boolean = false
    
    override fun getLayoutResource(): Int = R.layout.activity_login
    
    override fun initializeViews() {
        etUsername = findViewById(R.id.etUsername)
        etPassword = findViewById(R.id.etPassword)
        rgUserType = findViewById(R.id.rgUserType)
        rbCustomer = findViewById(R.id.rbCustomer)
        rbRider = findViewById(R.id.rbRider)
        btnLogin = findViewById(R.id.btnLogin)
        tvRegisterRider = findViewById(R.id.tvRegisterRider)
        progressBar = findViewById(R.id.progressBar)
        ivLogo = findViewById(R.id.ivLogo)
        tvTitle = findViewById(R.id.tvTitle)
        tvSubtitle = findViewById(R.id.tvSubtitle)
        
        loginViewModel = ViewModelProvider(this)[LoginViewModel::class.java]
        
        // Setup initial animations
        setupInitialAnimations()
    }
    
    override fun setupObservers() {
        loginViewModel.isLoading.observe(this) { isLoading ->
            if (isLoading) {
                animateButtonLoading(true)
                progressBar.visibility = android.view.View.VISIBLE
                btnLogin.isEnabled = false
            } else {
                animateButtonLoading(false)
                progressBar.visibility = android.view.View.GONE
                btnLogin.isEnabled = true
            }
        }
        
        loginViewModel.errorMessage.observe(this) { errorMessage ->
            errorMessage?.let {
                // Show appropriate error message with additional context
                when {
                    it.contains("approval", ignoreCase = true) -> {
                        showErrorDialog(
                            title = "Account Pending Approval",
                            message = it,
                            positiveAction = "Contact Support"
                        )
                    }
                    it.contains("suspended", ignoreCase = true) -> {
                        showErrorDialog(
                            title = "Account Suspended",
                            message = it,
                            positiveAction = "Contact Support"
                        )
                    }
                    it.contains("network", ignoreCase = true) || 
                    it.contains("connection", ignoreCase = true) ||
                    it.contains("internet", ignoreCase = true) -> {
                        showErrorDialog(
                            title = "Network Error",
                            message = it,
                            positiveAction = "Retry"
                        )
                    }
                    it.contains("invalid", ignoreCase = true) ||
                    it.contains("password", ignoreCase = true) ||
                    it.contains("username", ignoreCase = true) -> {
                        showErrorDialog(
                            title = "Login Failed",
                            message = it,
                            positiveAction = "Try Again"
                        )
                    }
                    else -> {
                        showErrorDialog(
                            title = "Login Error",
                            message = it,
                            positiveAction = "OK"
                        )
                    }
                }
                animateError()
                loginViewModel.clearError()
            }
        }
        
        loginViewModel.successMessage.observe(this) { successMessage ->
            successMessage?.let {
                showToast(it)
                loginViewModel.clearSuccess()
            }
        }
        loginViewModel.loginResponse.observe(this) { loginResponse ->
            loginResponse?.let {
                // Save session data using existing method
                loginResponse.user?.let { user ->
                    lifecycleScope.launch {
                        sessionManager.saveLoginSession(
                            user = com.onpointinfo.mobimeals.data.models.User(
                                id = user.id,
                                username = user.username,
                                firstName = user.firstName,
                                lastName = user.lastName,
                                email = user.email,
                                userType = user.userType
                            ),
                            accessToken = loginResponse.access_token ?: "",
                            refreshToken = loginResponse.refresh_token ?: ""
                        )
                        
                        // Trigger login success animation and navigation
                        animateSuccess()
                        Handler(Looper.getMainLooper()).postDelayed({
                            navigateToDashboard()
                        }, 1000)
                    }
                }
            }
        }
    }
    
    override fun setupListeners() {
        btnLogin.setOnClickListener {
            performLogin()
        }
        
        tvRegisterRider.setOnClickListener {
            animateClick(tvRegisterRider)
            startActivity(Intent(this, RiderRegisterActivity::class.java))
        }
        
        rgUserType.setOnCheckedChangeListener { _, checkedId ->
            when (checkedId) {
                R.id.rbCustomer -> {
                    animateUserTypeChange("Customer")
                    etUsername.hint = "Customer Email"
                }
                R.id.rbRider -> {
                    animateUserTypeChange("Rider")
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
    
    // Animation Methods
    private fun setupInitialAnimations() {
        // Initially hide all views
        ivLogo.visibility = View.INVISIBLE
        tvTitle.visibility = View.INVISIBLE
        tvSubtitle.visibility = View.INVISIBLE
        btnLogin.visibility = View.INVISIBLE
        tvRegisterRider.visibility = View.INVISIBLE
        
        // Start animations after a short delay
        Handler(Looper.getMainLooper()).postDelayed({
            animateLogoIn()
        }, 100)
    }
    
    private fun animateLogoIn() {
        ivLogo.visibility = View.VISIBLE
        ivLogo.alpha = 0f
        ivLogo.scaleX = 0f
        ivLogo.scaleY = 0f
        
        val scaleX = ObjectAnimator.ofFloat(ivLogo, "scaleX", 0f, 1f)
        val scaleY = ObjectAnimator.ofFloat(ivLogo, "scaleY", 0f, 1f)
        val alpha = ObjectAnimator.ofFloat(ivLogo, "alpha", 0f, 1f)
        
        val animatorSet = AnimatorSet()
        animatorSet.playTogether(scaleX, scaleY, alpha)
        animatorSet.interpolator = OvershootInterpolator(1.2f)
        animatorSet.duration = 800
        animatorSet.addListener(object : Animator.AnimatorListener {
            override fun onAnimationStart(animation: Animator) {}
            override fun onAnimationEnd(animation: Animator) {
                animateTitleIn()
            }
            override fun onAnimationCancel(animation: Animator) {}
            override fun onAnimationRepeat(animation: Animator) {}
        })
        animatorSet.start()
    }
    
    private fun animateTitleIn() {
        tvTitle.visibility = View.VISIBLE
        tvTitle.alpha = 0f
        tvTitle.translationY = -50f
        
        val alpha = ObjectAnimator.ofFloat(tvTitle, "alpha", 0f, 1f)
        val translationY = ObjectAnimator.ofFloat(tvTitle, "translationY", -50f, 0f)
        
        val animatorSet = AnimatorSet()
        animatorSet.playTogether(alpha, translationY)
        animatorSet.interpolator = AccelerateDecelerateInterpolator()
        animatorSet.duration = 600
        animatorSet.addListener(object : Animator.AnimatorListener {
            override fun onAnimationStart(animation: Animator) {}
            override fun onAnimationEnd(animation: Animator) {
                animateSubtitleIn()
            }
            override fun onAnimationCancel(animation: Animator) {}
            override fun onAnimationRepeat(animation: Animator) {}
        })
        animatorSet.start()
    }
    
    private fun animateSubtitleIn() {
        tvSubtitle.visibility = View.VISIBLE
        tvSubtitle.alpha = 0f
        tvSubtitle.translationY = -30f
        
        val alpha = ObjectAnimator.ofFloat(tvSubtitle, "alpha", 0f, 1f)
        val translationY = ObjectAnimator.ofFloat(tvSubtitle, "translationY", -30f, 0f)
        
        val animatorSet = AnimatorSet()
        animatorSet.playTogether(alpha, translationY)
        animatorSet.interpolator = AccelerateDecelerateInterpolator()
        animatorSet.duration = 500
        animatorSet.addListener(object : Animator.AnimatorListener {
            override fun onAnimationStart(animation: Animator) {}
            override fun onAnimationEnd(animation: Animator) {
                animateFormElementsIn()
            }
            override fun onAnimationCancel(animation: Animator) {}
            override fun onAnimationRepeat(animation: Animator) {}
        })
        animatorSet.start()
    }
    
    private fun animateFormElementsIn() {
        val userTypeParent = rgUserType.parent as View
        val usernameParent = etUsername.parent as View
        val passwordParent = etPassword.parent as View
        
        // Set initial states
        userTypeParent.visibility = View.VISIBLE
        userTypeParent.alpha = 0f
        userTypeParent.translationY = 50f
        
        usernameParent.visibility = View.VISIBLE
        usernameParent.alpha = 0f
        usernameParent.translationY = 50f
        
        passwordParent.visibility = View.VISIBLE
        passwordParent.alpha = 0f
        passwordParent.translationY = 50f
        
        btnLogin.visibility = View.VISIBLE
        btnLogin.alpha = 0f
        btnLogin.translationY = 50f
        
        tvRegisterRider.visibility = View.VISIBLE
        tvRegisterRider.alpha = 0f
        
        // Create animations
        val userTypeAlpha = ObjectAnimator.ofFloat(userTypeParent, "alpha", 0f, 1f)
        val userTypeTranslation = ObjectAnimator.ofFloat(userTypeParent, "translationY", 50f, 0f)
        
        val usernameAlpha = ObjectAnimator.ofFloat(usernameParent, "alpha", 0f, 1f)
        val usernameTranslation = ObjectAnimator.ofFloat(usernameParent, "translationY", 50f, 0f)
        
        val passwordAlpha = ObjectAnimator.ofFloat(passwordParent, "alpha", 0f, 1f)
        val passwordTranslation = ObjectAnimator.ofFloat(passwordParent, "translationY", 50f, 0f)
        
        val buttonAlpha = ObjectAnimator.ofFloat(btnLogin, "alpha", 0f, 1f)
        val buttonTranslation = ObjectAnimator.ofFloat(btnLogin, "translationY", 50f, 0f)
        
        val registerAlpha = ObjectAnimator.ofFloat(tvRegisterRider, "alpha", 0f, 1f)
        
        val userTypeSet = AnimatorSet()
        userTypeSet.playTogether(userTypeAlpha, userTypeTranslation)
        userTypeSet.duration = 400
        userTypeSet.interpolator = AccelerateDecelerateInterpolator()
        
        val usernameSet = AnimatorSet()
        usernameSet.playTogether(usernameAlpha, usernameTranslation)
        usernameSet.duration = 400
        usernameSet.interpolator = AccelerateDecelerateInterpolator()
        
        val passwordSet = AnimatorSet()
        passwordSet.playTogether(passwordAlpha, passwordTranslation)
        passwordSet.duration = 400
        passwordSet.interpolator = AccelerateDecelerateInterpolator()
        
        val buttonSet = AnimatorSet()
        buttonSet.playTogether(buttonAlpha, buttonTranslation)
        buttonSet.duration = 400
        buttonSet.interpolator = AccelerateDecelerateInterpolator()
        
        val registerSet = AnimatorSet()
        registerSet.playTogether(registerAlpha)
        registerSet.duration = 400
        registerSet.interpolator = AccelerateDecelerateInterpolator()
        
        userTypeSet.start()
        Handler(Looper.getMainLooper()).postDelayed({ usernameSet.start() }, 100)
        Handler(Looper.getMainLooper()).postDelayed({ passwordSet.start() }, 200)
        Handler(Looper.getMainLooper()).postDelayed({ buttonSet.start() }, 300)
        Handler(Looper.getMainLooper()).postDelayed({ registerSet.start() }, 400)
    }
    
    private fun animateButtonLoading(loading: Boolean) {
        if (loading) {
            val scaleX = ObjectAnimator.ofFloat(btnLogin, "scaleX", 1f, 0.95f)
            val scaleY = ObjectAnimator.ofFloat(btnLogin, "scaleY", 1f, 0.95f)
            val animatorSet = AnimatorSet()
            animatorSet.playTogether(scaleX, scaleY)
            animatorSet.duration = 200
            animatorSet.start()
        } else {
            val scaleX = ObjectAnimator.ofFloat(btnLogin, "scaleX", 0.95f, 1f)
            val scaleY = ObjectAnimator.ofFloat(btnLogin, "scaleY", 0.95f, 1f)
            val animatorSet = AnimatorSet()
            animatorSet.playTogether(scaleX, scaleY)
            animatorSet.duration = 200
            animatorSet.start()
        }
    }
    
    private fun animateError() {
        val shake = ObjectAnimator.ofFloat(etUsername.parent, "translationX", 0f, -20f, 20f, -20f, 20f, -10f, 10f, 0f)
        shake.duration = 500
        shake.start()
        
        val shake2 = ObjectAnimator.ofFloat(etPassword.parent, "translationX", 0f, -20f, 20f, -20f, 20f, -10f, 10f, 0f)
        shake2.duration = 500
        shake2.start()
    }
    
    private fun animateSuccess() {
        val scale = ObjectAnimator.ofFloat(ivLogo, "scaleX", 1f, 1.2f, 1f)
        scale.duration = 600
        scale.interpolator = AccelerateDecelerateInterpolator()
        scale.start()
    }
    
    private fun animateClick(view: View) {
        val scaleX = ObjectAnimator.ofFloat(view, "scaleX", 1f, 0.95f, 1f)
        val scaleY = ObjectAnimator.ofFloat(view, "scaleY", 1f, 0.95f, 1f)
        val animatorSet = AnimatorSet()
        animatorSet.playTogether(scaleX, scaleY)
        animatorSet.duration = 150
        animatorSet.start()
    }
    
    private fun animateUserTypeChange(userType: String) {
        val alpha = ObjectAnimator.ofFloat(tvSubtitle, "alpha", 1f, 0.3f, 1f)
        alpha.duration = 300
        alpha.start()
        
        tvSubtitle.text = when (userType) {
            "Customer" -> "Order delicious food"
            "Rider" -> "Deliver and earn"
            else -> "Fast Food Delivery"
        }
    }
    
    private fun getLoginErrorMessage(errorMessage: String): String {
        return when {
            errorMessage.contains("Invalid username or password") -> 
                "Incorrect username or password. Please try again."
            errorMessage.contains("Invalid credentials") -> 
                "Incorrect login details. Please check and try again."
            errorMessage.contains("User not found") -> 
                "Account not found. Please check your username or register."
            errorMessage.contains("403") || errorMessage.contains("Forbidden") -> 
                "Access denied. Please check your account status."
            errorMessage.contains("404") || errorMessage.contains("not found") -> 
                "Login service unavailable. Please try again later."
            errorMessage.contains("500") || errorMessage.contains("Internal Server Error") -> 
                "Server error. Please try again in a few minutes."
            errorMessage.contains("network") || errorMessage.contains("connection") -> 
                "Network error. Please check your internet connection."
            errorMessage.contains("timeout") -> 
                "Request timed out. Please try again."
            else -> "Login failed. Please try again later."
        }
    }
    
    private fun showErrorDialog(title: String, message: String, positiveAction: String) {
        val dialog = androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle(title)
            .setMessage(message)
            .setPositiveButton(positiveAction) { dialog, _ ->
                dialog.dismiss()
                when (positiveAction) {
                    "Retry" -> {
                        // Focus on username field for retry
                        etUsername.requestFocus()
                        etUsername.selectAll()
                    }
                    "Try Again" -> {
                        // Focus on username field for retry
                        etUsername.requestFocus()
                        etUsername.selectAll()
                    }
                    "Contact Support" -> {
                        // Could open email app or support page
                        showToast("Please contact our support team for assistance")
                    }
                    else -> {
                        // Just dismiss dialog
                    }
                }
            }
            .setNegativeButton("Cancel") { dialog, _ ->
                dialog.dismiss()
            }
            .setIcon(
                when (title) {
                    "Account Pending Approval" -> R.drawable.ic_info
                    "Account Suspended" -> R.drawable.ic_warning
                    "Network Error" -> R.drawable.ic_warning
                    "Login Failed" -> R.drawable.ic_error
                    else -> R.drawable.ic_info
                }
            )
            .create()
        
        dialog.show()
    }
}
