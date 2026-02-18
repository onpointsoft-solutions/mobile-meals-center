package com.arvind.mobilemealscenter

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material.MaterialTheme
import androidx.compose.material.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.arvind.mobilemealscenter.component.StandardScaffold
import com.arvind.mobilemealscenter.navigation.Navigation
import com.arvind.mobilemealscenter.navigation.Screen
import com.arvind.mobilemealscenter.ui.theme.MobileMealsCenterTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MobileMealsCenterTheme {
                // A surface container using the 'background' color from the theme
                MobileMealsCenterUIMain()
            }
        }
    }

    @Composable
    fun MobileMealsCenterUIMain() {
        MobileMealsCenterTheme {
            Surface(
                color = MaterialTheme.colors.background,
                modifier = Modifier.fillMaxSize()
            ) {
                val navController = rememberNavController()
                val navBackStackEntry by navController.currentBackStackEntryAsState()
                
                // Determine which screens show bottom bar
                val customerBottomBarScreens = listOf(
                    Screen.CustomerHomeScreen.route,
                    Screen.CustomerRestaurantsScreen.route,
                    Screen.CustomerOrdersScreen.route,
                    Screen.CustomerProfileScreen.route,
                )
                
                val riderBottomBarScreens = listOf(
                    Screen.RiderHomeScreen.route,
                    Screen.RiderAvailableOrdersScreen.route,
                    Screen.RiderActiveOrdersScreen.route,
                    Screen.RiderProfileScreen.route,
                )
                
                val showBottomBar = navBackStackEntry?.destination?.route in (customerBottomBarScreens + riderBottomBarScreens)
                
                StandardScaffold(
                    navController = navController,
                    showBottomBar = showBottomBar,
                    modifier = Modifier.fillMaxSize(),
                    onFabClick = {
                        navController.navigate(Screen.SearchScreen.route)
                    }
                ) {
                    Navigation(navController)
                }
            }
        }
    }
}

