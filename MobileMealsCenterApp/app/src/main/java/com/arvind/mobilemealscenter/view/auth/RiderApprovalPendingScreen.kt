package com.arvind.mobilemealscenter.view.auth

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
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController

@Composable
fun RiderApprovalPendingScreen(navController: NavController) {
    var isCheckingStatus by remember { mutableStateOf(false) }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        // Success Icon
        Icon(
            Icons.Default.CheckCircle,
            contentDescription = "Success",
            tint = Color(0xFF4CAF50),
            modifier = Modifier.size(80.dp)
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Title
        Text(
            text = "Registration Submitted!",
            fontSize = 28.sp,
            fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colors.primary
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Message
        Text(
            text = "Your rider registration has been submitted successfully.\n\nOur team will review your application and get back to you within 24-48 hours.\n\nYou will receive an email once your account is approved.",
            fontSize = 16.sp,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colors.onSurface.copy(alpha = 0.7f),
            lineHeight = 24.sp
        )
        
        Spacer(modifier = Modifier.height(32.dp))
        
        // Status Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(12.dp),
            elevation = 4.dp,
            backgroundColor = Color(0xFFFFF3E0)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(20.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(24.dp),
                        strokeWidth = 3.dp,
                        color = Color(0xFFFF9800)
                    )
                    Spacer(modifier = Modifier.width(12.dp))
                    Text(
                        text = "Approval Pending",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFFFF9800)
                    )
                }
                
                Spacer(modifier = Modifier.height(12.dp))
                
                Text(
                    text = "Your application is currently under review by our admin team.",
                    fontSize = 14.sp,
                    textAlign = TextAlign.Center,
                    color = MaterialTheme.colors.onSurface.copy(alpha = 0.7f)
                )
            }
        }
        
        Spacer(modifier = Modifier.height(32.dp))
        
        // What's Next Section
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
                    text = "What happens next?",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(bottom = 16.dp)
                )
                
                listOf(
                    "📧 You'll receive an email when your account is approved",
                    "📱 Download and install the Mobile Meals Center app",
                    "🚴 Complete your first delivery and start earning!",
                    "💰 Get paid weekly for all completed deliveries"
                ).forEach { item ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 4.dp)
                    ) {
                        Text(
                            text = item,
                            fontSize = 14.sp,
                            color = MaterialTheme.colors.onSurface.copy(alpha = 0.8f)
                        )
                    }
                }
            }
        }
        
        Spacer(modifier = Modifier.height(32.dp))
        
        // Action Buttons
        Column(
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Button(
                onClick = {
                    isCheckingStatus = true
                    // Here you would check approval status
                    // For now, just simulate checking
                },
                modifier = Modifier.fillMaxWidth(),
                enabled = !isCheckingStatus
            ) {
                if (isCheckingStatus) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(20.dp),
                        color = MaterialTheme.colors.onPrimary
                    )
                } else {
                    Text("Check Approval Status")
                }
            }
            
            OutlinedButton(
                onClick = { navController.navigate("welcome_screen") },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Back to Home")
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Contact Info
        Text(
            text = "Need help? Contact us at support@mobilemealscenter.co.ke",
            fontSize = 12.sp,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colors.onSurface.copy(alpha = 0.6f)
        )
    }
}
