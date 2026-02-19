package com.onpointinfo.mobimeals.rider

import android.content.Intent
import android.os.Bundle
import android.widget.*
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.onpointinfo.mobimeals.R
import com.onpointinfo.mobimeals.auth.LoginActivity
import com.onpointinfo.mobimeals.base.BaseActivity

class RiderDashboardActivity : BaseActivity() {
    
    private lateinit var riderDashboardViewModel: RiderDashboardViewModel
    private lateinit var tvWelcome: TextView
    private lateinit var tvOnlineStatus: TextView
    private lateinit var switchOnline: Switch
    private lateinit var tvTodayEarnings: TextView
    private lateinit var tvTodayDeliveries: TextView
    private lateinit var tvRating: TextView
    private lateinit var btnAvailableOrders: Button
    private lateinit var btnDeliveryHistory: Button
    private lateinit var btnProfile: Button
    private lateinit var btnLogout: Button
    private lateinit var progressBar: ProgressBar
    
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
                tvWelcome.text = "Welcome, ${it.user.firstName} ${it.user.lastName}"
                switchOnline.isChecked = it.isOnline
                updateOnlineStatus(it.isOnline)
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
            riderDashboardViewModel.toggleOnlineStatus(isChecked)
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
        if (isOnline) {
            tvOnlineStatus.text = "🟢 Online - Available for deliveries"
            tvOnlineStatus.setTextColor(getColor(R.color.colorSuccess))
        } else {
            tvOnlineStatus.text = "🔴 Offline - Not accepting orders"
            tvOnlineStatus.setTextColor(getColor(R.color.colorError))
        }
    }
    
    override fun onResume() {
        super.onResume()
        riderDashboardViewModel.loadRiderData()
    }
}
