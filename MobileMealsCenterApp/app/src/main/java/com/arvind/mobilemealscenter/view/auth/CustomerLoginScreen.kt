package com.arvind.mobilemealscenter.view.auth

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.arvind.mobilemealscenter.data.RetrofitClient
import com.arvind.mobilemealscenter.model.LoginRequest
import kotlinx.coroutines.launch

@Composable
fun CustomerLoginScreen(navController: NavController) {
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
            Icons.Default.Restaurant,
            contentDescription = "Customer",
            tint = MaterialTheme.colors.primary,
            modifier = Modifier.size(80.dp)
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Title
        Text(
            text = "Customer Login",
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
                                        // Check if user is a customer
                                        if (loginResponse.user.userType == "customer") {
                                            // Customer login successful, navigate to customer home
                                            navController.navigate("customer_home_screen") {
                                                popUpTo("welcome_screen") { inclusive = true }
                                            }
                                        } else {
                                            errorMessage = "This login is for customers only. Please select the correct user type."
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
                        Text("Login as Customer")
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
            TextButton(onClick = { navController.navigate("create_account_screen") }) {
                Text("Register")
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
            backgroundColor = MaterialTheme.colors.primary.copy(alpha = 0.1f),
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
                        tint = MaterialTheme.colors.primary,
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "Customer Features",
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colors.primary
                    )
                }
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Text(
                    text = "• Browse restaurants and menus\n• Track your orders in real-time\n• Save favorite restaurants\n• Rate and review meals",
                    fontSize = 12.sp,
                    color = MaterialTheme.colors.onSurface.copy(alpha = 0.8f),
                    lineHeight = 16.sp
                )
            }
        }
    }
}
