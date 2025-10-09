package com.financas.android

import android.app.Application
import com.financas.android.data.api.ApiClient
import io.sentry.Sentry

class FinancasApplication : Application() {

    override fun onCreate() {
        super.onCreate()
        ApiClient.initialize(this)

        Sentry.init {
            it.dsn = "YOUR_SENTRY_DSN"
            // Set tracesSampleRate to 1.0 to capture 100% of transactions for performance monitoring.
            // We recommend adjusting this value in production.
            it.tracesSampleRate = 1.0
        }
    }
}