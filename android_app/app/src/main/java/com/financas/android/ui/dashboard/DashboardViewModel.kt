package com.financas.android.ui.dashboard

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.financas.android.data.api.ApiClient
import com.financas.android.data.models.ContaBancaria
import com.financas.android.utils.Resource
import kotlinx.coroutines.launch

class DashboardViewModel : ViewModel() {

    private val _contas = MutableLiveData<Resource<List<ContaBancaria>>>()
    val contas: LiveData<Resource<List<ContaBancaria>>> = _contas

    fun getContas() {
        _contas.postValue(Resource.Loading())

        viewModelScope.launch {
            try {
                val response = ApiClient.apiService.getContas()

                if (response.isSuccessful && response.body() != null) {
                    _contas.postValue(Resource.Success(response.body()!!))
                } else {
                    val errorBody = response.errorBody()?.string() ?: "Failed to get contas"
                    _contas.postValue(Resource.Error(errorBody))
                }
            } catch (e: Exception) {
                _contas.postValue(Resource.Error(e.message ?: "An unexpected error occurred"))
            }
        }
    }
}