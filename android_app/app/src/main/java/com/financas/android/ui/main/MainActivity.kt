package com.financas.android.ui.main

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import com.financas.android.R
import com.financas.android.databinding.ActivityMainBinding
import com.financas.android.ui.dashboard.DashboardFragment
import com.financas.android.ui.profile.ProfileFragment
import com.financas.android.ui.transactions.TransactionsFragment

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        if (savedInstanceState == null) {
            supportFragmentManager.beginTransaction().replace(R.id.fragment_container, DashboardFragment()).commit()
        }

        binding.bottomNavigation.setOnItemSelectedListener { item ->
            var selectedFragment: Fragment? = null
            when (item.itemId) {
                R.id.navigation_dashboard -> selectedFragment = DashboardFragment()
                R.id.navigation_transactions -> selectedFragment = TransactionsFragment()
                R.id.navigation_profile -> selectedFragment = ProfileFragment()
            }
            if (selectedFragment != null) {
                supportFragmentManager.beginTransaction().replace(R.id.fragment_container, selectedFragment).commit()
            }
            true
        }
    }
}