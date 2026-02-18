package com.arvind.mobilemealscenter.view.customer

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.arvind.mobilemealscenter.data.RetrofitClient
import com.arvind.mobilemealscenter.model.Order
import kotlinx.coroutines.launch

@Composable
fun CustomerTrackOrderScreen(navController: NavController, orderId: String) {
    var order by remember { mutableStateOf<Order?>(null) }
    var isLoading by remember { mutableStateOf(true) }
    val coroutineScope = rememberCoroutineScope()
    
    // Load order details
    LaunchedEffect(orderId) {
        coroutineScope.launch {
            try {
                val response = RetrofitClient.apiService.getOrder("Bearer token", orderId.toInt()) // Replace with actual token
                if (response.isSuccessful) {
                    order = response.body()
                }
            } catch (e: Exception) {
                // Handle error
            } finally {
                isLoading = false
            }
        }
    }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        // Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = { navController.popBackStack() }) {
                Icon(Icons.Default.ArrowBack, contentDescription = "Back")
            }
            
            Text(
                text = "Track Order",
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold
            )
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        if (isLoading) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else if (order != null) {
            // Order Status Timeline
            OrderStatusTimeline(currentStatus = order!!.status)
            
            Spacer(modifier = Modifier.height(24.dp))
            
            // Order Details Card
            OrderDetailsCard(order = order!!)
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Delivery Information Card
            DeliveryInfoCard(order = order!!)
            
            Spacer(modifier = Modifier.height(16.dp))
            
            // Contact Support Button
            Button(
                onClick = { /* Contact support */ },
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp)
            ) {
                Icon(Icons.Default.Phone, contentDescription = "Call")
                Spacer(modifier = Modifier.width(8.dp))
                Text("Contact Support")
            }
        }
    }
}

@Composable
fun OrderStatusTimeline(currentStatus: String) {
    val statusSteps = listOf(
        "pending" to "Order Placed",
        "confirmed" to "Order Confirmed", 
        "preparing" to "Preparing Food",
        "ready" to "Ready for Delivery",
        "delivering" to "Out for Delivery",
        "delivered" to "Delivered"
    )
    
    val currentIndex = statusSteps.indexOfFirst { it.first == currentStatus }
    
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        elevation = 4.dp
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp)
        ) {
            Text(
                text = "Order Status",
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(bottom = 16.dp)
            )
            
            statusSteps.forEachIndexed { index, (status, title) ->
                val isCompleted = index <= currentIndex
                val isCurrent = index == currentIndex
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // Status Circle
                    Box(
                        modifier = Modifier.size(24.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        if (isCompleted) {
                            Icon(
                                Icons.Default.CheckCircle,
                                contentDescription = null,
                                tint = if (isCurrent) MaterialTheme.colors.primary else Color(0xFF4CAF50),
                                modifier = Modifier.size(24.dp)
                            )
                        } else {
                            Icon(
                                Icons.Default.Circle,
                                contentDescription = null,
                                tint = Color.Gray,
                                modifier = Modifier.size(24.dp)
                            )
                        }
                    }
                    
                    // Status Line
                    if (index < statusSteps.size - 1) {
                        Box(
                            modifier = Modifier
                                .width(2.dp)
                                .height(40.dp)
                                .padding(start = 11.dp)
                        ) {
                            Divider(
                                color = if (isCompleted) Color(0xFF4CAF50) else Color.Gray,
                                thickness = 2.dp
                            )
                        }
                    }
                    
                    Spacer(modifier = Modifier.width(16.dp))
                    
                    // Status Text
                    Column {
                        Text(
                            text = title,
                            fontSize = 14.sp,
                            fontWeight = if (isCurrent) FontWeight.Bold else FontWeight.Normal,
                            color = if (isCurrent) MaterialTheme.colors.primary else MaterialTheme.colors.onSurface
                        )
                    }
                }
                
                if (index < statusSteps.size - 1) {
                    Spacer(modifier = Modifier.height(8.dp))
                }
            }
        }
    }
}

@Composable
fun OrderDetailsCard(order: Order) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        elevation = 4.dp
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Text(
                text = "Order Details",
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(bottom = 12.dp)
            )
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "Order #${order.order_number}",
                    fontSize = 14.sp,
                    color = MaterialTheme.colors.onSurface.copy(alpha = 0.7f)
                )
                Text(
                    text = "KES ${order.total_amount}",
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colors.primary
                )
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = order.restaurant.name,
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium
            )
            
            Text(
                text = "${order.items.size} items",
                fontSize = 12.sp,
                color = MaterialTheme.colors.onSurface.copy(alpha = 0.6f)
            )
        }
    }
}

@Composable
fun DeliveryInfoCard(order: Order) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        elevation = 4.dp
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Text(
                text = "Delivery Information",
                fontSize = 16.sp,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.padding(bottom = 12.dp)
            )
            
            Row(
                verticalAlignment = Alignment.Top
            ) {
                Icon(
                    Icons.Default.LocationOn,
                    contentDescription = "Address",
                    tint = MaterialTheme.colors.primary,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = order.delivery_address,
                    fontSize = 14.sp,
                    modifier = Modifier.weight(1f)
                )
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    Icons.Default.Phone,
                    contentDescription = "Phone",
                    tint = MaterialTheme.colors.primary,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = order.phone,
                    fontSize = 14.sp
                )
            }
            
            if (order.special_instructions?.isNotEmpty() == true) {
                Spacer(modifier = Modifier.height(8.dp))
                
                Row(
                    verticalAlignment = Alignment.Top
                ) {
                    Icon(
                        Icons.Default.Note,
                        contentDescription = "Notes",
                        tint = MaterialTheme.colors.primary,
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = order.special_instructions,
                        fontSize = 14.sp,
                        modifier = Modifier.weight(1f)
                    )
                }
            }
        }
    }
}
