package com.financas.android.ui.auth

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.financas.android.data.storage.SessionManager
import com.financas.android.databinding.ActivityLoginBinding
import com.financas.android.ui.main.MainActivity
import com.financas.android.utils.Resource

class LoginActivity : AppCompatActivity() {

    private lateinit var binding: ActivityLoginBinding
    private val viewModel: LoginViewModel by viewModels()
    private lateinit var sessionManager: SessionManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityLoginBinding.inflate(layoutInflater)
        setContentView(binding.root)

        sessionManager = SessionManager(this)

        setupClickListeners()
        setupObservers()
    }

    private fun setupClickListeners() {
        binding.buttonLogin.setOnClickListener {
            handleLogin()
        }

        binding.textViewRegister.setOnClickListener {
            // TODO: Navigate to RegisterActivity
            Toast.makeText(this, "Navigate to Register screen", Toast.LENGTH_SHORT).show()
        }

        binding.textViewForgotPassword.setOnClickListener {
            // TODO: Navigate to Forgot Password screen
            Toast.makeText(this, "Navigate to Forgot Password screen", Toast.LENGTH_SHORT).show()
        }
    }

    private fun setupObservers() {
        viewModel.loginResult.observe(this) { resource ->
            when (resource) {
                is Resource.Loading -> {
                    binding.progressBar.visibility = View.VISIBLE
                    binding.buttonLogin.isEnabled = false
                }
                is Resource.Success -> {
                    binding.progressBar.visibility = View.GONE
                    binding.buttonLogin.isEnabled = true
                    Toast.makeText(this, "Login successful!", Toast.LENGTH_LONG).show()
                    sessionManager.saveAuthTokens(resource.data.access, resource.data.refresh)
                    val intent = Intent(this, MainActivity::class.java)
                    startActivity(intent)
                    finish()
                }
                is Resource.Error -> {
                    binding.progressBar.visibility = View.GONE
                    binding.buttonLogin.isEnabled = true
                    Toast.makeText(this, "Error: ${resource.message}", Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    private fun handleLogin() {
        val username = binding.editTextUsername.text.toString().trim()
        val password = binding.editTextPassword.text.toString().trim()

        if (username.isEmpty() || password.isEmpty()) {
            Toast.makeText(this, "Usuário e senha são obrigatórios", Toast.LENGTH_SHORT).show()
            return
        }

        viewModel.login(username, password)
    }
}