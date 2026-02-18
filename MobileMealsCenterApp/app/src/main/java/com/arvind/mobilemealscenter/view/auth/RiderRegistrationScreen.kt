package com.arvind.mobilemealscenter.view.auth

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
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
import com.arvind.mobilemealscenter.model.RegisterRequest
import kotlinx.coroutines.launch

@Composable
fun RiderRegistrationScreen(navController: NavController) {
    var isLoading by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf("") }
    val coroutineScope = rememberCoroutineScope()
    
    // Basic registration fields
    var username by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var confirmPassword by remember { mutableStateOf("") }
    var firstName by remember { mutableStateOf("") }
    var lastName by remember { mutableStateOf("") }
    var phone by remember { mutableStateOf("") }
    
    // Rider profile fields
    var idNumber by remember { mutableStateOf("") }
    var vehicleType by remember { mutableStateOf("motorcycle") }
    var vehicleNumber by remember { mutableStateOf("") }
    var emergencyContact by remember { mutableStateOf("") }
    var bankAccount by remember { mutableStateOf("") }
    var bankName by remember { mutableStateOf("") }
    
    val vehicleTypes = listOf("bicycle", "motorcycle", "car")
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .verticalScroll(rememberScrollState()),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Header
        Text(
            text = "Become a Delivery Rider",
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.align(Alignment.CenterHorizontally)
        )
        
        Text(
            text = "Join our team and start earning!",
            fontSize = 14.sp,
            color = MaterialTheme.colors.onSurface.copy(alpha = 0.7f),
            modifier = Modifier.align(Alignment.CenterHorizontally)
        )
        
        // Basic Information Section
        Card(
            modifier = Modifier.fillMaxWidth(),
            elevation = 4.dp
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Text(
                    text = "Basic Information",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )
                
                // Name fields
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    OutlinedTextField(
                        value = firstName,
                        onValueChange = { firstName = it },
                        label = { Text("First Name") },
                        modifier = Modifier.weight(1f)
                    )
                    OutlinedTextField(
                        value = lastName,
                        onValueChange = { lastName = it },
                        label = { Text("Last Name") },
                        modifier = Modifier.weight(1f)
                    )
                }
                
                OutlinedTextField(
                    value = username,
                    onValueChange = { username = it },
                    label = { Text("Username") },
                    modifier = Modifier.fillMaxWidth()
                )
                
                OutlinedTextField(
                    value = email,
                    onValueChange = { email = it },
                    label = { Text("Email") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
                    modifier = Modifier.fillMaxWidth()
                )
                
                OutlinedTextField(
                    value = phone,
                    onValueChange = { phone = it },
                    label = { Text("Phone Number") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
                    modifier = Modifier.fillMaxWidth()
                )
                
                OutlinedTextField(
                    value = password,
                    onValueChange = { password = it },
                    label = { Text("Password") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                    modifier = Modifier.fillMaxWidth()
                )
                
                OutlinedTextField(
                    value = confirmPassword,
                    onValueChange = { confirmPassword = it },
                    label = { Text("Confirm Password") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }
        
        // Rider Profile Section
        Card(
            modifier = Modifier.fillMaxWidth(),
            elevation = 4.dp
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Text(
                    text = "Rider Profile",
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )
                
                OutlinedTextField(
                    value = idNumber,
                    onValueChange = { idNumber = it },
                    label = { Text("ID Number") },
                    modifier = Modifier.fillMaxWidth()
                )
                
                // Vehicle Type
                Text(
                    text = "Vehicle Type",
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Medium
                )
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    vehicleTypes.forEach { type ->
                        FilterChip(
                            onClick = { vehicleType = type },
                            selected = vehicleType == type,
                            label = { Text(type.capitalize()) },
                            modifier = Modifier.weight(1f)
                        )
                    }
                }
                
                OutlinedTextField(
                    value = vehicleNumber,
                    onValueChange = { vehicleNumber = it },
                    label = { Text("Vehicle Number") },
                    modifier = Modifier.fillMaxWidth()
                )
                
                OutlinedTextField(
                    value = emergencyContact,
                    onValueChange = { emergencyContact = it },
                    label = { Text("Emergency Contact") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
                    modifier = Modifier.fillMaxWidth()
                )
                
                OutlinedTextField(
                    value = bankAccount,
                    onValueChange = { bankAccount = it },
                    label = { Text("Bank Account Number") },
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    modifier = Modifier.fillMaxWidth()
                )
                
                OutlinedTextField(
                    value = bankName,
                    onValueChange = { bankName = it },
                    label = { Text("Bank Name") },
                    modifier = Modifier.fillMaxWidth()
                )
            }
        }
        
        // Error Message
        if (errorMessage.isNotEmpty()) {
            Text(
                text = errorMessage,
                color = MaterialTheme.colors.error,
                modifier = Modifier.align(Alignment.CenterHorizontally)
            )
        }
        
        // Register Button
        Button(
            onClick = {
                if (password != confirmPassword) {
                    errorMessage = "Passwords do not match"
                    return@Button
                }
                
                if (firstName.isEmpty() || lastName.isEmpty() || username.isEmpty() || 
                    email.isEmpty() || phone.isEmpty() || idNumber.isEmpty() || 
                    vehicleNumber.isEmpty()) {
                    errorMessage = "Please fill all required fields"
                    return@Button
                }
                
                isLoading = true
                errorMessage = ""
                
                coroutineScope.launch {
                    try {
                        val registerRequest = RegisterRequest(
                            username = username,
                            email = email,
                            password = password,
                            firstName = firstName,
                            lastName = lastName,
                            phone = phone,
                            userType = "rider",
                            id_number = idNumber,
                            vehicle_type = vehicleType,
                            vehicle_number = vehicleNumber,
                            emergency_contact = emergencyContact,
                            bank_account = bankAccount,
                            bank_name = bankName
                        )
                        
                        val response = RetrofitClient.apiService.register(registerRequest)
                        if (response.isSuccessful) {
                            // Registration successful, navigate to approval waiting screen
                            navController.navigate("rider_approval_pending_screen")
                        } else {
                            errorMessage = "Registration failed. Please try again."
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
                Text("Register as Rider")
            }
        }
        
        // Login Link
        Row(
            modifier = Modifier.align(Alignment.CenterHorizontally),
            horizontalArrangement = Arrangement.Center
        ) {
            Text("Already have an account? ")
            TextButton(onClick = { navController.popBackStack() }) {
                Text("Login")
            }
        }
    }
}

@OptIn(ExperimentalMaterialApi::class)
@Composable
fun FilterChip(
    onClick: () -> Unit,
    selected: Boolean,
    label: @Composable () -> Unit,
    modifier: Modifier = Modifier
) {
    FilterChip(
        selected = selected,
        onClick = onClick,
        label = label,
        modifier = modifier,
        colors = FilterChipDefaults.filterChipColors(
            selectedBackgroundColor = MaterialTheme.colors.primary.copy(alpha = 0.2f),
            selectedContentColor = MaterialTheme.colors.primary
        )
    )
}
