package com.onpointinfo.mobimeals.network

import okhttp3.Interceptor
import okhttp3.Response
import okhttp3.Request
import java.util.HashMap

class CookieInterceptor : Interceptor {
    
    private val cookieStore = HashMap<String, String>()
    
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        
        // Add cookies and headers to request
        val cookieHeader = buildCookieHeader()
        var requestBuilder = request.newBuilder()
        
        // Add cookies if available
        if (cookieHeader.isNotEmpty()) {
            requestBuilder.addHeader("Cookie", cookieHeader)
        }
        
        // Add Django-specific headers for CSRF compliance
        if (request.url.encodedPath.contains("login")) {
            requestBuilder
                .addHeader("Referer", "https://mobilemealscenter.co.ke/accounts/login/")
                .addHeader("Origin", "https://mobilemealscenter.co.ke")
                .addHeader("User-Agent", "MobileMeals-Android-App/1.0")
        } else if (request.url.encodedPath.contains("api/")) {
            // Add headers for all API requests to prevent CSRF issues
            val apiRequestBuilder = requestBuilder
                .addHeader("Referer", "https://mobilemealscenter.co.ke/")
                .addHeader("Origin", "https://mobilemealscenter.co.ke")
                .addHeader("User-Agent", "MobileMeals-Android-App/1.0")
                .addHeader("X-Requested-With", "XMLHttpRequest")
            
            // Add CSRF token if available (for POST, PUT, DELETE requests)
            if (request.method in listOf("POST", "PUT", "DELETE", "PATCH")) {
                val csrfToken = getCookie("csrftoken")
                if (csrfToken != null) {
                    apiRequestBuilder.addHeader("X-CSRFToken", csrfToken)
                    println("DEBUG: Added CSRF token to API request: $csrfToken")
                } else {
                    println("DEBUG: No CSRF token found, trying without it (backend should have @csrf_exempt)")
                    // Add a dummy CSRF token to prevent Django from rejecting the request entirely
                    // This will work if @csrf_exempt is deployed on the backend
                    apiRequestBuilder.addHeader("X-CSRFToken", "dummy-token-for-testing")
                }
            }
            
            requestBuilder = apiRequestBuilder
        }
        
        val requestWithHeaders = requestBuilder.build()
        val response = chain.proceed(requestWithHeaders)
        
        // Store cookies from response
        response.headers("Set-Cookie").forEach { cookie ->
            val cookieParts = cookie.split(";")
            val mainPart = cookieParts[0]
            val keyValue = mainPart.split("=", limit = 2)
            if (keyValue.size == 2) {
                val cookieName = keyValue[0].trim()
                val cookieValue = keyValue[1].trim()
                cookieStore[cookieName] = cookieValue
                
                // Debug logging for important cookies
                if (cookieName == "csrftoken" || cookieName == "sessionid") {
                    println("DEBUG: Stored cookie: $cookieName=$cookieValue")
                }
            }
        }
        
        return response
    }
    
    private fun buildCookieHeader(): String {
        // Prioritize CSRF token and session cookies
        val prioritizedCookies = listOf("csrftoken", "sessionid", "messages")
        val cookieList = mutableListOf<String>()
        
        // Add prioritized cookies first
        prioritizedCookies.forEach { cookieName ->
            cookieStore[cookieName]?.let { value ->
                cookieList.add("$cookieName=$value")
            }
        }
        
        // Add remaining cookies
        cookieStore.forEach { (name, value) ->
            if (!prioritizedCookies.contains(name)) {
                cookieList.add("$name=$value")
            }
        }
        
        return cookieList.joinToString("; ")
    }
    
    fun clearCookies() {
        cookieStore.clear()
        println("DEBUG: All cookies cleared")
    }
    
    fun getCookie(name: String): String? {
        return cookieStore[name]
    }
    
    fun ensureCsrfToken(): String? {
        // Return existing CSRF token if available
        getCookie("csrftoken")?.let { return it }
        
        // If no CSRF token, we could make a request to get one
        // For now, return null and let the request proceed (may work if @csrf_exempt is deployed)
        println("DEBUG: No CSRF token available, hoping @csrf_exempt is deployed")
        return null
    }
}
