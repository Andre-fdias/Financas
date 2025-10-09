package com.financas.android.data.api

import com.financas.android.data.models.*
import retrofit2.Response
import retrofit2.http.*

interface ApiService {

    @POST("auth/token/")
    suspend fun login(@Body request: LoginRequest): Response<LoginResponse>

    @POST("auth/token/refresh/")
    suspend fun refreshToken(@Body request: RefreshTokenRequest): Response<LoginResponse>

    @GET("contas/")
    suspend fun getContas(): Response<List<ContaBancaria>>

    @GET("categorias/")
    suspend fun getCategorias(): Response<List<Categoria>>

    @GET("subcategorias/")
    suspend fun getSubcategorias(): Response<List<Subcategoria>>

    @GET("entradas/")
    suspend fun getEntradas(): Response<List<Entrada>>

    @GET("saidas/")
    suspend fun getSaidas(): Response<List<Saida>>

    @GET("transacoes/")
    suspend fun getTransactions(): Response<List<Transaction>>

    @DELETE("transacoes/{id}/")
    suspend fun deleteTransaction(@Path("id") id: Int): Response<Unit>

    @GET("profile/")
    suspend fun getProfile(): Response<Profile>

    @GET("relatorios/")
    suspend fun getReports(): Response<List<Report>>
}
