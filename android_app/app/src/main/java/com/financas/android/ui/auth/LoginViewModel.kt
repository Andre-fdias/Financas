package com.financas.android.ui.auth

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.financas.android.data.api.ApiClient
import com.financas.android.data.models.LoginRequest
import com.financas.android.data.models.LoginResponse
import com.financas.android.utils.Resource
import kotlinx.coroutines.launch

class LoginViewModel : ViewModel() {

    private val _loginResult = MutableLiveData<Resource<LoginResponse>>()
    val loginResult: LiveData<Resource<LoginResponse>> = _loginResult

    fun login(username: String, password: String) {
        _loginResult.postValue(Resource.Loading())

        viewModelScope.launch {
            try {
                val request = LoginRequest(username, password)
                val response = ApiClient.apiService.login(request)

                if (response.isSuccessful && response.body() != null) {
                    _loginResult.postValue(Resource.Success(response.body()!!))
                } else {
                    // Handle specific error messages from the API if available
                    val errorBody = response.errorBody()?.string() ?: "Authentication Failed"
                    _loginResult.postValue(Resource.Error(errorBody))
                }
            } catch (e: Exception) {
                // Handle network errors or other exceptions
                _loginResult.postValue(Resource.Error(e.message ?: "An unexpected error occurred"))
            }
        }
    }
}
