package com.onpointinfo.mobimeals.rider

import android.os.Bundle
import android.widget.*
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.onpointinfo.mobimeals.R
import com.onpointinfo.mobimeals.base.BaseActivity

class AvailableOrdersActivity : BaseActivity() {
    
    private lateinit var availableOrdersViewModel: AvailableOrdersViewModel
    private lateinit var recyclerView: RecyclerView
    private lateinit var tvEmptyState: TextView
    private lateinit var progressBar: ProgressBar
    private lateinit var btnBack: ImageButton
    private lateinit var btnRefresh: Button
    private lateinit var availableOrdersAdapter: AvailableOrdersAdapter
    
    override fun getLayoutResource(): Int = R.layout.activity_available_orders
    
    override fun initializeViews() {
        recyclerView = findViewById(R.id.recyclerView)
        tvEmptyState = findViewById(R.id.tvEmptyState)
        progressBar = findViewById(R.id.progressBar)
        btnBack = findViewById(R.id.btnBack)
        btnRefresh = findViewById(R.id.btnRefresh)
        
        availableOrdersViewModel = ViewModelProvider(this)[AvailableOrdersViewModel::class.java]
        
        setupRecyclerView()
    }
    
    override fun setupObservers() {
        availableOrdersViewModel.isLoading.observe(this) { isLoading ->
            progressBar.visibility = if (isLoading) android.view.View.VISIBLE else android.view.View.GONE
            btnRefresh.isEnabled = !isLoading
        }
        
        availableOrdersViewModel.errorMessage.observe(this) { errorMessage ->
            errorMessage?.let {
                when {
                    it.contains("online", ignoreCase = true) -> {
                        // Show dialog for online status requirement
                        androidx.appcompat.app.AlertDialog.Builder(this)
                            .setTitle("Online Status Required")
                            .setMessage("You must be online to view available orders. Would you like to go online now?")
                            .setPositiveButton("Go Online") { dialog, _ ->
                                dialog.dismiss()
                                // Navigate back to dashboard to toggle online status
                                finish()
                            }
                            .setNegativeButton("Cancel") { dialog, _ ->
                                dialog.dismiss()
                            }
                            .setIcon(R.drawable.ic_info)
                            .show()
                    }
                    it.contains("network", ignoreCase = true) || 
                    it.contains("connection", ignoreCase = true) ||
                    it.contains("internet", ignoreCase = true) -> {
                        // Show network error dialog
                        androidx.appcompat.app.AlertDialog.Builder(this)
                            .setTitle("Network Error")
                            .setMessage(it)
                            .setPositiveButton("Retry") { dialog, _ ->
                                dialog.dismiss()
                                availableOrdersViewModel.loadAvailableOrders()
                            }
                            .setNegativeButton("Cancel") { dialog, _ ->
                                dialog.dismiss()
                            }
                            .setIcon(R.drawable.ic_warning)
                            .show()
                    }
                    else -> {
                        showToast(it)
                    }
                }
                availableOrdersViewModel.clearError()
            }
        }
        
        availableOrdersViewModel.successMessage.observe(this) { successMessage ->
            successMessage?.let {
                // Show success message for empty state
                tvEmptyState.text = it
                availableOrdersViewModel.clearSuccess()
            }
        }
        
        availableOrdersViewModel.availableOrders.observe(this) { orders ->
            if (orders.isEmpty()) {
                recyclerView.visibility = android.view.View.GONE
                tvEmptyState.visibility = android.view.View.VISIBLE
            } else {
                recyclerView.visibility = android.view.View.VISIBLE
                tvEmptyState.visibility = android.view.View.GONE
                availableOrdersAdapter.submitList(orders)
            }
        }
    }
    
    override fun setupListeners() {
        btnBack.setOnClickListener {
            finish()
        }
        
        btnRefresh.setOnClickListener {
            availableOrdersViewModel.loadAvailableOrders()
        }
    }
    
    private fun setupRecyclerView() {
        availableOrdersAdapter = AvailableOrdersAdapter { order ->
            // Handle order acceptance
            availableOrdersViewModel.acceptOrder(order.id)
        }
        
        recyclerView.apply {
            layoutManager = LinearLayoutManager(this@AvailableOrdersActivity)
            adapter = availableOrdersAdapter
        }
    }
    
    override fun onResume() {
        super.onResume()
        availableOrdersViewModel.loadAvailableOrders()
    }
}
