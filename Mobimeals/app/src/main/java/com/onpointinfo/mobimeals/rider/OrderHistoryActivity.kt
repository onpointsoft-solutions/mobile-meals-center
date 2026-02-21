package com.onpointinfo.mobimeals.rider

import android.os.Bundle
import android.widget.*
import androidx.appcompat.widget.AppCompatImageButton
import androidx.lifecycle.ViewModelProvider
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.onpointinfo.mobimeals.R
import com.onpointinfo.mobimeals.base.BaseActivity

class OrderHistoryActivity : BaseActivity() {
    
    private lateinit var orderHistoryViewModel: OrderHistoryViewModel
    private lateinit var recyclerView: RecyclerView
    private lateinit var tvEmptyState: TextView
    private lateinit var progressBar: ProgressBar
    private lateinit var btnBack: AppCompatImageButton
    private lateinit var orderHistoryAdapter: OrderHistoryAdapter
    
    override fun getLayoutResource(): Int = R.layout.activity_order_history
    
    override fun initializeViews() {
        recyclerView = findViewById(R.id.recyclerView)
        tvEmptyState = findViewById(R.id.tvEmptyState)
        progressBar = findViewById(R.id.progressBar)
        btnBack = findViewById(R.id.btnBack)
        
        orderHistoryViewModel = ViewModelProvider(this)[OrderHistoryViewModel::class.java]
        
        setupRecyclerView()
    }
    
    override fun setupObservers() {
        orderHistoryViewModel.isLoading.observe(this) { isLoading ->
            progressBar.visibility = if (isLoading) android.view.View.VISIBLE else android.view.View.GONE
        }
        
        orderHistoryViewModel.errorMessage.observe(this) { errorMessage ->
            errorMessage?.let {
                showToast(it)
                orderHistoryViewModel.clearError()
            }
        }
        
        orderHistoryViewModel.orderHistory.observe(this) { orders ->
            if (orders.isEmpty()) {
                recyclerView.visibility = android.view.View.GONE
                tvEmptyState.visibility = android.view.View.VISIBLE
            } else {
                recyclerView.visibility = android.view.View.VISIBLE
                tvEmptyState.visibility = android.view.View.GONE
                orderHistoryAdapter.submitList(orders)
            }
        }
    }
    
    override fun setupListeners() {
        btnBack.setOnClickListener {
            finish()
        }
    }
    
    private fun setupRecyclerView() {
        orderHistoryAdapter = OrderHistoryAdapter { order ->
            // Handle order item click if needed
            showToast("Order: ${order.id}")
        }
        
        recyclerView.apply {
            layoutManager = LinearLayoutManager(this@OrderHistoryActivity)
            adapter = orderHistoryAdapter
        }
    }
    
    override fun onResume() {
        super.onResume()
        orderHistoryViewModel.loadOrderHistory()
    }
}
