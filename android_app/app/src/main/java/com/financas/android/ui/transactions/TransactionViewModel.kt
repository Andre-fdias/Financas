package com.financas.android.ui.transactions

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.financas.android.data.api.ApiClient
import com.financas.android.data.models.Transaction
import com.financas.android.utils.Resource
import kotlinx.coroutines.launch

class TransactionViewModel : ViewModel() {

    private val _transactions = MutableLiveData<Resource<List<Transaction>>>()
    val transactions: LiveData<Resource<List<Transaction>>> = _transactions

    private val _transactionDeleted = MutableLiveData<Resource<Unit>>()
    val transactionDeleted: LiveData<Resource<Unit>> = _transactionDeleted

    fun getTransactions() {
        _transactions.postValue(Resource.Loading())

        viewModelScope.launch {
            try {
                val response = ApiClient.apiService.getTransactions()

                if (response.isSuccessful && response.body() != null) {
                    _transactions.postValue(Resource.Success(response.body()!!))
                } else {
                    val errorBody = response.errorBody()?.string() ?: "Failed to get transactions"
                    _transactions.postValue(Resource.Error(errorBody))
                }
            } catch (e: Exception) {
                _transactions.postValue(Resource.Error(e.message ?: "An unexpected error occurred"))
            }
        }
    }

    fun deleteTransaction(id: Int) {
        _transactionDeleted.postValue(Resource.Loading())

        viewModelScope.launch {
            try {
                val response = ApiClient.apiService.deleteTransaction(id)

                if (response.isSuccessful) {
                    _transactionDeleted.postValue(Resource.Success(Unit))
                } else {
                    val errorBody = response.errorBody()?.string() ?: "Failed to delete transaction"
                    _transactionDeleted.postValue(Resource.Error(errorBody))
                }
            } catch (e: Exception) {
                _transactionDeleted.postValue(Resource.Error(e.message ?: "An unexpected error occurred"))
            }
        }
    }
}