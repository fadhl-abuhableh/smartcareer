package com.example.smartcareer.adapters


import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.smartcareer.R
import com.example.smartcareer.models.Milestone

class MilestoneAdapter(private val milestoneList: List<Milestone>) :
    RecyclerView.Adapter<MilestoneAdapter.MilestoneViewHolder>() {

    class MilestoneViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val tvTitle: TextView = itemView.findViewById(R.id.tvMilestoneTitle)
        val tvDate: TextView = itemView.findViewById(R.id.tvMilestoneDate)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MilestoneViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.milestone_card, parent, false)
        return MilestoneViewHolder(view)
    }

    override fun onBindViewHolder(holder: MilestoneViewHolder, position: Int) {
        val milestone = milestoneList[position]
        holder.tvTitle.text = milestone.title
        holder.tvDate.text = milestone.date
    }

    override fun getItemCount(): Int = milestoneList.size
}
