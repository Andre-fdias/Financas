package com.financas.android.ui.reports

import android.os.Bundle
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.financas.android.data.models.Report
import com.financas.android.databinding.ActivityReportsBinding
import com.financas.android.utils.Resource
import com.github.mikephil.charting.data.BarData
import com.github.mikephil.charting.data.BarDataSet
import com.github.mikephil.charting.data.BarEntry

class ReportsActivity : AppCompatActivity() {

    private lateinit var binding: ActivityReportsBinding
    private val viewModel: ReportsViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityReportsBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupObservers()
        viewModel.getReports()
    }

    private fun setupObservers() {
        viewModel.reports.observe(this) { resource ->
            when (resource) {
                is Resource.Loading -> {
                    // Show progress bar
                }
                is Resource.Success -> {
                    // Hide progress bar
                    setupChart(resource.data)
                }
                is Resource.Error -> {
                    // Hide progress bar
                    Toast.makeText(this, "Error: ${resource.message}", Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    private fun setupChart(data: List<Report>) {
        val entries = ArrayList<BarEntry>()
        for ((index, report) in data.withIndex()) {
            entries.add(BarEntry(index.toFloat(), report.total_entradas.toFloat()))
        }

        val dataSet = BarDataSet(entries, "Entradas")
        val barData = BarData(dataSet)
        binding.barChart.data = barData
        binding.barChart.invalidate()
    }
}