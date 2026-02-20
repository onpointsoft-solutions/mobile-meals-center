package com.onpointinfo.mobimeals.rider

import android.content.Intent
import android.os.Bundle
import android.widget.*
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.switchmaterial.SwitchMaterial
import com.onpointinfo.mobimeals.R
import com.onpointinfo.mobimeals.auth.LoginActivity
import com.onpointinfo.mobimeals.base.BaseActivity

class RiderDashboardActivity : BaseActivity() {
    
    private lateinit var riderDashboardViewModel: RiderDashboardViewModel
    private lateinit var tvWelcome: TextView
    private lateinit var tvOnlineStatus: TextView
    private lateinit var switchOnline: SwitchMaterial
    private lateinit var tvTodayEarnings: TextView
    private lateinit var tvTodayDeliveries: TextView
    private lateinit var tvRating: TextView
    private lateinit var btnAvailableOrders: LinearLayout
    private lateinit var btnDeliveryHistory: LinearLayout
    private lateinit var btnProfile: Button
    private lateinit var btnLogout: Button
    private lateinit var progressBar: ProgressBar
    
    // Flag to prevent switch listener conflicts
    private var isUpdatingSwitch = false
    
    override fun getLayoutResource(): Int = R.layout.activity_rider_dashboard
    
    override fun initializeViews() {
        tvWelcome = findViewById(R.id.tvWelcome)
        tvOnlineStatus = findViewById(R.id.tvOnlineStatus)
        switchOnline = findViewById(R.id.switchOnline)
        tvTodayEarnings = findViewById(R.id.tvTodayEarnings)
        tvTodayDeliveries = findViewById(R.id.tvTodayDeliveries)
        tvRating = findViewById(R.id.tvRating)
        btnAvailableOrders = findViewById(R.id.btnAvailableOrders)
        btnDeliveryHistory = findViewById(R.id.btnDeliveryHistory)
        btnProfile = findViewById(R.id.btnProfile)
        btnLogout = findViewById(R.id.btnLogout)
        progressBar = findViewById(R.id.progressBar)
        
        riderDashboardViewModel = ViewModelProvider(this)[RiderDashboardViewModel::class.java]
        riderDashboardViewModel.setSessionManager(sessionManager)
    }
    
    override fun setupObservers() {
        riderDashboardViewModel.isLoading.observe(this) { isLoading ->
            progressBar.visibility = if (isLoading) android.view.View.VISIBLE else android.view.View.GONE
        }
        
        riderDashboardViewModel.errorMessage.observe(this) { errorMessage ->
            errorMessage?.let {
                showToast(it)
                riderDashboardViewModel.clearError()
            }
        }
        
        riderDashboardViewModel.successMessage.observe(this) { successMessage ->
            successMessage?.let {
                showToast(it)
                riderDashboardViewModel.clearSuccess()
            }
        }
        
        riderDashboardViewModel.riderProfile.observe(this) { profile ->
            profile?.let {
                println("DEBUG: RiderProfile updated - isOnline: ${it.isOnline}")
                tvWelcome.text = "Welcome, ${it.user.firstName ?: it.user.username}"
                
                // Update switch position only if different to prevent infinite loops
                if (switchOnline.isChecked != it.isOnline) {
                    println("DEBUG: Updating switch from ${switchOnline.isChecked} to ${it.isOnline}")
                    isUpdatingSwitch = true
                    switchOnline.isChecked = it.isOnline
                    isUpdatingSwitch = false
                } else {
                    println("DEBUG: Switch already at correct position: ${it.isOnline}")
                }
                
                // Update status text and appearance
                updateOnlineStatus(it.isOnline)
                
                println("DEBUG: Updated UI with online status: ${it.isOnline}")
            }
        }
        
        riderDashboardViewModel.earningsData.observe(this) { earnings ->
            earnings?.let {
                tvTodayEarnings.text = "Today's Earnings: $${String.format("%.2f", it.todayEarnings)}"
                tvTodayDeliveries.text = "Today's Deliveries: ${it.totalDeliveries}"
                tvRating.text = "Rating: ${String.format("%.1f", it.averageRating)}⭐"
            }
        }
    }
    
    override fun setupListeners() {
        switchOnline.setOnCheckedChangeListener { _, isChecked ->
            if (!isUpdatingSwitch) {
                println("DEBUG: Switch changed by user to: $isChecked")
                riderDashboardViewModel.toggleOnlineStatus(isChecked)
            } else {
                println("DEBUG: Switch change ignored due to programmatic update")
            }
        }
        
        btnAvailableOrders.setOnClickListener {
            startActivity(Intent(this, AvailableOrdersActivity::class.java))
        }
        
        btnDeliveryHistory.setOnClickListener {
            startActivity(Intent(this, OrderHistoryActivity::class.java))
        }
        
        btnProfile.setOnClickListener {
            showToast("Profile management coming soon")
        }
        
        btnLogout.setOnClickListener {
            logoutUser()
        }
    }
    
    private fun updateOnlineStatus(isOnline: Boolean) {
        println("DEBUG: updateOnlineStatus called with isOnline: $isOnline")
        
        if (isOnline) {
            tvOnlineStatus.text = "🟢 Online - Available for deliveries"
            tvOnlineStatus.setTextColor(getColor(R.color.white))
            tvOnlineStatus.backgroundTintList = getColorStateList(R.color.colorSuccess)
            
            // Also update switch appearance
            switchOnline.thumbTintList = getColorStateList(R.color.colorSuccess)
            switchOnline.trackTintList = getColorStateList(R.color.colorSuccess)
            
            println("DEBUG: Set status to Online with green theme")
        } else {
            tvOnlineStatus.text = "🔴 Offline - Not accepting orders"
            tvOnlineStatus.setTextColor(getColor(R.color.white))
            tvOnlineStatus.backgroundTintList = getColorStateList(R.color.colorError)
            
            // Also update switch appearance
            switchOnline.thumbTintList = getColorStateList(R.color.colorError)
            switchOnline.trackTintList = getColorStateList(R.color.colorError)
            
            println("DEBUG: Set status to Offline with red theme")
        }
        
        println("DEBUG: Status text updated to: ${tvOnlineStatus.text}")
    }
    
    override fun onResume() {
        super.onResume()
        riderDashboardViewModel.loadRiderData()
    }
}
