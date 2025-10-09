package com.financas.android.ui.reports

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.financas.android.data.api.ApiClient
import com.financas.android.data.models.Report
import com.financas.android.utils.Resource
import kotlinx.coroutines.launch

class ReportsViewModel : ViewModel() {

    private val _reports = MutableLiveData<Resource<List<Report>>>()
    val reports: LiveData<Resource<List<Report>>> = _reports

    fun getReports() {
        _reports.postValue(Resource.Loading())

        viewModelScope.launch {
            try {
                val response = ApiClient.apiService.getReports()

                if (response.isSuccessful && response.body() != null) {
                    _reports.postValue(Resource.Success(response.body()!!))
                } else {
                    val errorBody = response.errorBody()?.string() ?: "Failed to get reports"
                    _reports.postValue(Resource.Error(errorBody))
                }
            } catch (e: Exception) {
                _reports.postValue(Resource.Error(e.message ?: "An unexpected error occurred"))
            }
        }
    }
}