package com.financas.android.ui.profile

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.financas.android.data.api.ApiClient
import com.financas.android.data.models.Profile
import com.financas.android.utils.Resource
import kotlinx.coroutines.launch

class ProfileViewModel : ViewModel() {

    private val _profile = MutableLiveData<Resource<Profile>>()
    val profile: LiveData<Resource<Profile>> = _profile

    fun getProfile() {
        _profile.postValue(Resource.Loading())

        viewModelScope.launch {
            try {
                val response = ApiClient.apiService.getProfile()

                if (response.isSuccessful && response.body() != null) {
                    _profile.postValue(Resource.Success(response.body()!!))
                } else {
                    val errorBody = response.errorBody()?.string() ?: "Failed to get profile"
                    _profile.postValue(Resource.Error(errorBody))
                }
            } catch (e: Exception) {
                _profile.postValue(Resource.Error(e.message ?: "An unexpected error occurred"))
            }
        }
    }
}