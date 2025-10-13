package com.financas.android.data.api

import android.content.Context
import com.financas.android.data.models.RefreshTokenRequest
import com.financas.android.data.storage.SessionManager
import kotlinx.coroutines.runBlocking
import okhttp3.Authenticator
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.Route
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object ApiClient {

    // Use 10.0.2.2 for the Android emulator to connect to localhost
    private const val BASE_URL = "http://10.0.2.2:8000/api/v1/"

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }

    // We need a context to access the SessionManager, so we will have to initialize it later
    private var retrofit: Retrofit? = null
    val apiService: ApiService
        get() = retrofit!!.create(ApiService::class.java)

    fun initialize(context: Context) {
        if (retrofit == null) {
            val httpClient = OkHttpClient.Builder()
                .addInterceptor(loggingInterceptor)
                .addInterceptor(AuthInterceptor(context))
                .authenticator(AuthAuthenticator(context))
                .build()

            retrofit = Retrofit.Builder()
                .baseUrl(BASE_URL)
                .client(httpClient)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
        }
    }
}

class AuthAuthenticator(context: Context) : Authenticator {

    private val sessionManager = SessionManager(context)

    override fun authenticate(route: Route?, response: Response): Request? {
        val refreshToken = sessionManager.getRefreshToken() ?: return null

        return runBlocking {
            val tokenResponse = ApiClient.apiService.refreshToken(RefreshTokenRequest(refreshToken))

            if (tokenResponse.isSuccessful && tokenResponse.body() != null) {
                sessionManager.saveAuthTokens(tokenResponse.body()!!.access, tokenResponse.body()!!.refresh)
                response.request.newBuilder()
                    .header("Authorization", "Bearer ${tokenResponse.body()!!.access}")
                    .build()
            } else {
                null
            }
        }
    }
}
