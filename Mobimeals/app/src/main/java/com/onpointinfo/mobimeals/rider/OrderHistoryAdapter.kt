package com.onpointinfo.mobimeals.rider

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.onpointinfo.mobimeals.R
import com.onpointinfo.mobimeals.data.models.DeliveryAssignment
import java.text.SimpleDateFormat
import java.util.*

class OrderHistoryAdapter(
    private val onOrderClick: (DeliveryAssignment) -> Unit
) : RecyclerView.Adapter<OrderHistoryAdapter.OrderHistoryViewHolder>() {
    
    private var orders = emptyList<DeliveryAssignment>()
    private val dateFormat = SimpleDateFormat("MMM dd, yyyy", Locale.getDefault())
    private val timeFormat = SimpleDateFormat("hh:mm a", Locale.getDefault())
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): OrderHistoryViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_order_history, parent, false)
        return OrderHistoryViewHolder(view)
    }
    
    override fun onBindViewHolder(holder: OrderHistoryViewHolder, position: Int) {
        holder.bind(orders[position])
    }
    
    override fun getItemCount(): Int = orders.size
    
    fun submitList(newOrders: List<DeliveryAssignment>) {
        orders = newOrders
        notifyDataSetChanged()
    }
    
    inner class OrderHistoryViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val tvOrderNumber: TextView = itemView.findViewById(R.id.tvOrderNumber)
        private val tvRestaurantName: TextView = itemView.findViewById(R.id.tvRestaurantName)
        private val tvCustomerName: TextView = itemView.findViewById(R.id.tvCustomerName)
        private val tvDeliveryAddress: TextView = itemView.findViewById(R.id.tvDeliveryAddress)
        private val tvStatus: TextView = itemView.findViewById(R.id.tvStatus)
        private val tvAssignedAt: TextView = itemView.findViewById(R.id.tvAssignedAt)
        private val tvDeliveredAt: TextView = itemView.findViewById(R.id.tvDeliveredAt)
        private val tvEarnings: TextView = itemView.findViewById(R.id.tvEarnings)
        
        fun bind(assignment: DeliveryAssignment) {
            tvOrderNumber.text = "Order #${assignment.order.orderNumber}"
            tvRestaurantName.text = assignment.order.restaurant.name
            tvCustomerName.text = assignment.order.customer.username
            tvDeliveryAddress.text = assignment.order.deliveryAddress
            tvStatus.text = assignment.status.replace("_", " ").uppercase()
            
            // Format dates
            tvAssignedAt.text = "Assigned: ${formatDate(assignment.assignedAt)}"
            tvDeliveredAt.text = assignment.deliveredAt?.let { 
                "Delivered: ${formatDate(it)}" 
            } ?: "Not delivered"
            
            // Set status color
            setStatusColor(assignment.status)
            
            // Show earnings if available
            tvEarnings.text = "Earnings: $${assignment.order.totalAmount}"
            
            itemView.setOnClickListener {
                onOrderClick(assignment)
            }
        }
        
        private fun formatDate(timestamp: String): String {
            return try {
                val date = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.getDefault())
                    .parse(timestamp)
                val calendar = Calendar.getInstance()
                calendar.time = date
                dateFormat.format(calendar.time) + " at " + timeFormat.format(calendar.time)
            } catch (e: Exception) {
                timestamp
            }
        }
        
        private fun setStatusColor(status: String) {
            val color = when (status.lowercase()) {
                "assigned" -> R.color.colorInfo
                "picked up" -> R.color.colorWarning
                "delivered" -> R.color.colorSuccess
                "cancelled" -> R.color.colorError
                else -> R.color.textSecondary
            }
            tvStatus.setTextColor(itemView.context.getColor(color))
        }
    }
}
