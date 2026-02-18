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
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import com.arvind.mobilemealscenter.data.RetrofitClient
import com.arvind.mobilemealscenter.model.LoginRequest
import kotlinx.coroutines.launch

@Composable
fun RiderLoginScreen(navController: NavController) {
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf("") }
    val coroutineScope = rememberCoroutineScope()
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        // Logo/Icon
        Icon(
            Icons.Default.DeliveryDining,
            contentDescription = "Rider",
            tint = MaterialTheme.colors.primary,
            modifier = Modifier.size(80.dp)
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Title
        Text(
            text = "Rider Login",
            fontSize = 28.sp,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colors.primary
        )
        
        Spacer(modifier = Modifier.height(8.dp))
        
        Text(
            text = "Mobile Meals Center",
            fontSize = 16.sp,
            color = MaterialTheme.colors.onSurface.copy(alpha = 0.7f)
        )
        
        Spacer(modifier = Modifier.height(32.dp))
        
        // Login Form
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(16.dp),
            elevation = 8.dp
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(24.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                Text(
                    text = "Welcome Back!",
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold
                )
                
                OutlinedTextField(
                    value = username,
                    onValueChange = { username = it },
                    label = { Text("Username or Email") },
                    leadingIcon = { Icon(Icons.Default.Person, contentDescription = "User") },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )
                
                OutlinedTextField(
                    value = password,
                    onValueChange = { password = it },
                    label = { Text("Password") },
                    leadingIcon = { Icon(Icons.Default.Lock, contentDescription = "Password") },
                    keyboardOptions = KeyboardType(keyboardType = KeyboardType.Password),
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true
                )
                
                // Error Message
                if (errorMessage.isNotEmpty()) {
                    Text(
                        text = errorMessage,
                        color = MaterialTheme.colors.error,
                        fontSize = 14.sp,
                        modifier = Modifier.align(Alignment.CenterHorizontally)
                    )
                }
                
                Button(
                    onClick = {
                        if (username.isEmpty() || password.isEmpty()) {
                            errorMessage = "Please fill all fields"
                            return@Button
                        }
                        
                        isLoading = true
                        errorMessage = ""
                        
                        coroutineScope.launch {
                            try {
                                val loginRequest = LoginRequest(
                                    username = username,
                                    password = password
                                )
                                
                                val response = RetrofitClient.apiService.login(loginRequest)
                                if (response.isSuccessful) {
                                    val loginResponse = response.body()
                                    if (loginResponse != null) {
                                        // Check if user is a rider and approved
                                        if (loginResponse.user.userType == "rider") {
                                            if (loginResponse.user.is_approved) {
                                                // Rider is approved, navigate to rider home
                                                navController.navigate("rider_home_screen") {
                                                    popUpTo("welcome_screen") { inclusive = true }
                                                }
                                            } else {
                                                // Rider not approved, show pending screen
                                                when (loginResponse.user.approval_status) {
                                                    "pending" -> {
                                                        navController.navigate("rider_approval_pending_screen") {
                                                            popUpTo("welcome_screen") { inclusive = true }
                                                        }
                                                    }
                                                    "rejected" -> {
                                                        errorMessage = "Your application was rejected. Please contact support."
                                                    }
                                                    else -> {
                                                        errorMessage = "Account status unknown. Please contact support."
                                                    }
                                                }
                                            }
                                        } else {
                                            errorMessage = "This login is for riders only. Please select the correct user type."
                                        }
                                    } else {
                                        errorMessage = "Login failed. Invalid response."
                                    }
                                } else {
                                    errorMessage = "Invalid username or password"
                                }
                            } catch (e: Exception) {
                                errorMessage = "Network error. Please check your connection."
                            } finally {
                                isLoading = false
                            }
                        }
                    },
                    modifier = Modifier.fillMaxWidth(),
                    enabled = !isLoading
                ) {
                    if (isLoading) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(20.dp),
                            color = MaterialTheme.colors.onPrimary
                        )
                    } else {
                        Text("Login as Rider")
                    }
                }
                
                // Forgot Password
                TextButton(
                    onClick = { navController.navigate("forgot_password_screen") },
                    modifier = Modifier.align(Alignment.CenterHorizontally)
                ) {
                    Text("Forgot Password?")
                }
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Register Link
        Row(
            horizontalArrangement = Arrangement.Center,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Don't have an account? ",
                color = MaterialTheme.colors.onSurface.copy(alpha = 0.7f)
            )
            TextButton(onClick = { navController.navigate("rider_registration_screen") }) {
                Text("Register as Rider")
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        // Back to User Type Selection
        TextButton(
            onClick = { navController.popBackStack() },
            modifier = Modifier.align(Alignment.CenterHorizontally)
        ) {
            Text("← Back to User Selection")
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Info Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(12.dp),
            backgroundColor = Color(0xFFE3F2FD),
            elevation = 2.dp
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp)
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        Icons.Default.Info,
                        contentDescription = "Info",
                        tint = Color(0xFF1976D2),
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "Rider Requirements",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF1976D2)
                    )
                }
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Text(
                    text = "• Valid ID document required\n• Vehicle registration needed\n• Background check performed\n• Approval process: 24-48 hours",
                    fontSize = 12.sp,
                    color = MaterialTheme.colors.onSurface.copy(alpha = 0.8f),
                    lineHeight = 16.sp
                )
            }
        }
    }
}
