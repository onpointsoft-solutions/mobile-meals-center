package com.onpointinfo.mobimeals.rider

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.onpointinfo.mobimeals.R
import com.onpointinfo.mobimeals.data.models.Order
import java.text.SimpleDateFormat
import java.util.*

class AvailableOrdersAdapter(
    private val onOrderAccept: (Order) -> Unit
) : RecyclerView.Adapter<AvailableOrdersAdapter.AvailableOrderViewHolder>() {
    
    private var orders = emptyList<Order>()
    private val dateFormat = SimpleDateFormat("MMM dd, yyyy", Locale.getDefault())
    private val timeFormat = SimpleDateFormat("hh:mm a", Locale.getDefault())
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): AvailableOrderViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_available_order, parent, false)
        return AvailableOrderViewHolder(view)
    }
    
    override fun onBindViewHolder(holder: AvailableOrderViewHolder, position: Int) {
        holder.bind(orders[position])
    }
    
    override fun getItemCount(): Int = orders.size
    
    fun submitList(newOrders: List<Order>) {
        orders = newOrders
        notifyDataSetChanged()
    }
    
    inner class AvailableOrderViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val tvOrderNumber: TextView = itemView.findViewById(R.id.tvOrderNumber)
        private val tvRestaurantName: TextView = itemView.findViewById(R.id.tvRestaurantName)
        private val tvCustomerName: TextView = itemView.findViewById(R.id.tvCustomerName)
        private val tvDeliveryAddress: TextView = itemView.findViewById(R.id.tvDeliveryAddress)
        private val tvTotalAmount: TextView = itemView.findViewById(R.id.tvTotalAmount)
        private val tvEstimatedTime: TextView = itemView.findViewById(R.id.tvEstimatedTime)
        private val tvOrderTime: TextView = itemView.findViewById(R.id.tvOrderTime)
        private val btnAccept: Button = itemView.findViewById(R.id.btnAccept)
        
        fun bind(order: Order) {
            tvOrderNumber.text = "Order #${order.orderNumber}"
            tvRestaurantName.text = order.restaurant.name
            tvCustomerName.text = "Customer: ${order.customer.username}"
            tvDeliveryAddress.text = "📍 ${order.deliveryAddress}"
            tvTotalAmount.text = "Total: $${order.totalAmount}"
            tvEstimatedTime.text = "Est. delivery: ${order.estimatedDeliveryTime ?: "30 mins"}"
            tvOrderTime.text = "Placed: ${formatDate(order.createdAt)}"
            
            btnAccept.setOnClickListener {
                onOrderAccept(order)
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
    }
}
