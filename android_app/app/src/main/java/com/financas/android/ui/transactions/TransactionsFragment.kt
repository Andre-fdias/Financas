package com.financas.android.ui.transactions

import android.content.Intent
import android.os.Bundle
import android.view.*
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.view.ActionMode
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.financas.android.R
import com.financas.android.data.models.Transaction
import com.financas.android.databinding.FragmentTransactionsBinding
import com.financas.android.utils.Resource

class TransactionsFragment : Fragment() {

    private var _binding: FragmentTransactionsBinding? = null
    private val binding get() = _binding!!

    private val viewModel: TransactionViewModel by viewModels()
    private lateinit var transactionAdapter: TransactionAdapter
    private var actionMode: ActionMode? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentTransactionsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupRecyclerView()
        setupObservers()

        binding.fab.setOnClickListener {
            val intent = Intent(requireContext(), AddTransactionActivity::class.java)
            startActivity(intent)
        }

        viewModel.getTransactions()
    }

    private fun setupRecyclerView() {
        transactionAdapter = TransactionAdapter { transaction ->
            if (actionMode == null) {
                actionMode = (activity as? AppCompatActivity)?.startSupportActionMode(ActionModeCallback(transaction))
            }
        }
        binding.recyclerView.apply {
            adapter = transactionAdapter
            layoutManager = LinearLayoutManager(requireContext())
        }
    }

    private fun setupObservers() {
        viewModel.transactions.observe(viewLifecycleOwner) { resource ->
            when (resource) {
                is Resource.Loading -> {
                    binding.progressBar.visibility = View.VISIBLE
                }
                is Resource.Success -> {
                    binding.progressBar.visibility = View.GONE
                    transactionAdapter.submitList(resource.data)
                }
                is Resource.Error -> {
                    binding.progressBar.visibility = View.GONE
                    Toast.makeText(requireContext(), "Error: ${resource.message}", Toast.LENGTH_LONG).show()
                }
            }
        }

        viewModel.transactionDeleted.observe(viewLifecycleOwner) { resource ->
            when (resource) {
                is Resource.Loading -> {
                    binding.progressBar.visibility = View.VISIBLE
                }
                is Resource.Success -> {
                    binding.progressBar.visibility = View.GONE
                    Toast.makeText(requireContext(), "Transação excluída com sucesso", Toast.LENGTH_SHORT).show()
                    viewModel.getTransactions() // Refresh the list
                }
                is Resource.Error -> {
                    binding.progressBar.visibility = View.GONE
                    Toast.makeText(requireContext(), "Error: ${resource.message}", Toast.LENGTH_LONG).show()
                }
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }

    private inner class ActionModeCallback(private val transaction: Transaction) : ActionMode.Callback {
        override fun onCreateActionMode(mode: ActionMode, menu: Menu): Boolean {
            val inflater = mode.menuInflater
            inflater.inflate(R.menu.transaction_context_menu, menu)
            return true
        }

        override fun onPrepareActionMode(mode: ActionMode, menu: Menu): Boolean {
            return false
        }

        override fun onActionItemClicked(mode: ActionMode, item: MenuItem): Boolean {
            return when (item.itemId) {
                R.id.action_edit -> {
                    // TODO: Navegar para a tela de edição
                    Toast.makeText(requireContext(), "Editar ${transaction.descricao}", Toast.LENGTH_SHORT).show()
                    mode.finish()
                    true
                }
                R.id.action_delete -> {
                    showDeleteConfirmationDialog(transaction)
                    mode.finish()
                    true
                }
                else -> false
            }
        }

        override fun onDestroyActionMode(mode: ActionMode) {
            actionMode = null
        }
    }

    private fun showDeleteConfirmationDialog(transaction: Transaction) {
        AlertDialog.Builder(requireContext())
            .setTitle("Excluir Transação")
            .setMessage("Você tem certeza que deseja excluir a transação \"${transaction.descricao}\"?")
            .setPositiveButton("Excluir") { _, _ ->
                viewModel.deleteTransaction(transaction.id)
            }
            .setNegativeButton("Cancelar", null)
            .show()
    }
}

class TransactionAdapter(private val onTransactionLongClick: (Transaction) -> Unit) : RecyclerView.Adapter<TransactionAdapter.TransactionViewHolder>() {

    private var transactions: List<Transaction> = emptyList()

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): TransactionViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_transaction, parent, false)
        return TransactionViewHolder(view)
    }

    override fun onBindViewHolder(holder: TransactionViewHolder, position: Int) {
        val transaction = transactions[position]
        holder.bind(transaction)
        holder.itemView.setOnLongClickListener {
            onTransactionLongClick(transaction)
            true
        }
    }

    override fun getItemCount(): Int = transactions.size

    fun submitList(transactions: List<Transaction>?) {
        this.transactions = transactions ?: emptyList()
        notifyDataSetChanged()
    }

    class TransactionViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val descriptionTextView: TextView = itemView.findViewById(R.id.descriptionTextView)
        private val valueTextView: TextView = itemView.findViewById(R.id.valueTextView)

        fun bind(transaction: Transaction) {
            descriptionTextView.text = transaction.descricao
            valueTextView.text = transaction.valor
        }
    }
}