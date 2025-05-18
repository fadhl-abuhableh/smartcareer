package com.example.smartcareer.adapters


import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.smartcareer.R
import com.example.smartcareer.models.Internship

class InternshipAdapter(private val internshipList: List<Internship>) :
    RecyclerView.Adapter<InternshipAdapter.InternshipViewHolder>() {

    class InternshipViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val tvCompany: TextView = itemView.findViewById(R.id.tvCompany)
        val tvRole: TextView = itemView.findViewById(R.id.tvRole)
        val tvDates: TextView = itemView.findViewById(R.id.tvDates)
        val tvDescription: TextView = itemView.findViewById(R.id.tvDescription)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): InternshipViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.internship_card, parent, false)
        return InternshipViewHolder(view)
    }

    override fun onBindViewHolder(holder: InternshipViewHolder, position: Int) {
        val internship = internshipList[position]
        holder.tvCompany.text = internship.company
        holder.tvRole.text = internship.role
        holder.tvDates.text = internship.dates
        holder.tvDescription.text = internship.description
    }

    override fun getItemCount(): Int = internshipList.size
}
