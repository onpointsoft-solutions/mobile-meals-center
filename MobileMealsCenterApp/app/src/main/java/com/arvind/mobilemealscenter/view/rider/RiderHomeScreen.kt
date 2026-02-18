package com.arvind.mobilemealscenter.view.rider

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import com.arvind.mobilemealscenter.model.DeliveryAssignment
import com.arvind.mobilemealscenter.model.Order
import kotlinx.coroutines.launch

@Composable
fun RiderHomeScreen(navController: NavController) {
    var availableOrders by remember { mutableStateOf<List<Order>>(emptyList()) }
    var activeDeliveries by remember { mutableStateOf<List<DeliveryAssignment>>(emptyList()) }
    var isLoading by remember { mutableStateOf(true) }
    val coroutineScope = rememberCoroutineScope()
    
    // Load data
    LaunchedEffect(Unit) {
        coroutineScope.launch {
            try {
                // Get available orders (ready for delivery)
                val availableResponse = RetrofitClient.apiService.getAvailableOrders("Bearer token") // Replace with actual token
                if (availableResponse.isSuccessful) {
                    availableOrders = availableResponse.body() ?: emptyList()
                }
                
                // Get active deliveries
                val activeResponse = RetrofitClient.apiService.getActiveOrders("Bearer token") // Replace with actual token
                if (activeResponse.isSuccessful) {
                    activeDeliveries = activeResponse.body() ?: emptyList()
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
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    text = "Rider Dashboard",
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "Mobile Meals Center",
                    fontSize = 14.sp,
                    color = MaterialTheme.colors.onSurface.copy(alpha = 0.7f)
                )
            }
            
            Row {
                // Online Status Toggle
                IconButton(onClick = { /* Toggle online status */ }) {
                    Icon(
                        Icons.Default.Circle,
                        contentDescription = "Online Status",
                        tint = Color(0xFF4CAF50) // Green for online
                    )
                }
                
                IconButton(onClick = { navController.navigate("rider_profile_screen") }) {
                    Icon(Icons.Default.Person, contentDescription = "Profile")
                }
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Stats Cards
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            StatCard(
                title = "Available",
                value = availableOrders.size.toString(),
                icon = Icons.Default.ShoppingCart,
                color = Color(0xFF4CAF50)
            )
            
            StatCard(
                title = "Active",
                value = activeDeliveries.size.toString(),
                icon = Icons.Default.DeliveryDining,
                color = Color(0xFF2196F3)
            )
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Quick Actions
        Text(
            text = "Quick Actions",
            fontSize = 18.sp,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(bottom = 12.dp)
        )
        
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            ActionButton(
                text = "Available Orders",
                icon = Icons.Default.ShoppingCart,
                onClick = { navController.navigate("rider_available_orders_screen") },
                modifier = Modifier.weight(1f)
            )
            
            ActionButton(
                text = "My Deliveries",
                icon = Icons.Default.DeliveryDining,
                onClick = { navController.navigate("rider_active_orders_screen") },
                modifier = Modifier.weight(1f)
            )
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Recent Activity
        Text(
            text = "Recent Activity",
            fontSize = 18.sp,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(bottom = 12.dp)
        )
        
        if (isLoading) {
            Box(
                modifier = Modifier.fillMaxWidth(),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else {
            LazyColumn(
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                // Show recent deliveries
                items(activeDeliveries.take(3)) { delivery ->
                    DeliveryCard(delivery = delivery, navController = navController)
                }
            }
        }
    }
}

@Composable
fun StatCard(
    title: String,
    value: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    color: Color
) {
    Card(
        modifier = Modifier
            .weight(1f)
            .height(80.dp),
        shape = RoundedCornerShape(12.dp),
        backgroundColor = color.copy(alpha = 0.1f),
        elevation = 2.dp
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Icon(
                imageVector = icon,
                contentDescription = title,
                tint = color,
                modifier = Modifier.size(24.dp)
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = value,
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = color
            )
            Text(
                text = title,
                fontSize = 12.sp,
                color = MaterialTheme.colors.onSurface.copy(alpha = 0.7f)
            )
        }
    }
}

@Composable
fun ActionButton(
    text: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Button(
        onClick = onClick,
        modifier = modifier.height(50.dp),
        shape = RoundedCornerShape(12.dp)
    ) {
        Icon(icon, contentDescription = null, modifier = Modifier.size(20.dp))
        Spacer(modifier = Modifier.width(8.dp))
        Text(text)
    }
}

@Composable
fun DeliveryCard(delivery: DeliveryAssignment, navController: NavController) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        elevation = 2.dp
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "Order #${delivery.order.id}",
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = delivery.status.replace("_", " ").capitalize(),
                    color = when (delivery.status) {
                        "assigned" -> Color(0xFFFF9800)
                        "picked_up" -> Color(0xFF2196F3)
                        "delivering" -> Color(0xFF9C27B0)
                        "delivered" -> Color(0xFF4CAF50)
                        else -> Color.Gray
                    }
                )
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = delivery.order.restaurant.name,
                fontSize = 14.sp,
                color = MaterialTheme.colors.onSurface.copy(alpha = 0.7f)
            )
            
            Text(
                text = delivery.order.delivery_address,
                fontSize = 12.sp,
                color = MaterialTheme.colors.onSurface.copy(alpha = 0.6f)
            )
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Button(
                onClick = { 
                    navController.navigate("rider_order_detail_screen/${delivery.id}")
                },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("View Details", fontSize = 12.sp)
            }
        }
    }
}
