package com.financas.android.data.models

import java.util.Date

data class Saida(
    val id: Int,
    val valor: String,
    val data: Date,
    val descricao: String,
    val categoria: Int,
    val conta_bancaria: Int,
    val usuario: Int
)