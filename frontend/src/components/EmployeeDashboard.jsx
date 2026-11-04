import React, { useState, useEffect } from "react";
import { Plus, Send, Edit2, Trash2 } from "lucide-react";
import { fetchExpenses, createExpense, updateExpense, deleteExpense, submitExpense } from "../api/endpoints";
import StatusBadge from "./StatusBadge";
import ExpenseModal from "./ExpenseModal";

export default function EmployeeDashboard() {
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingExpense, setEditingExpense] = useState(null);

  const loadExpenses = async () => {
    try {
      setLoading(true);
      const res = await fetchExpenses();
      setExpenses(res.data);
    } catch (err) {
      console.error("Failed to load expenses:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadExpenses();
  }, []);

  const handleSave = async (data) => {
    if (editingExpense) {
      await updateExpense(editingExpense.id, data);
    } else {
      await createExpense(data);
    }
    loadExpenses();
  };

  const handleSubmitExpense = async (id) => {
    if (!confirm("Are you sure you want to submit this expense for approval?")) return;
    try {
      await submitExpense(id);
      loadExpenses();
    } catch (err) {
      alert(err.response?.data?.detail || "Could not submit expense.");
    }
  };

  const handleDelete = async (id) => {
    if (!confirm("Are you sure you want to delete this draft?")) return;
    try {
      await deleteExpense(id);
      loadExpenses();
    } catch (err) {
      alert(err.response?.data?.detail || "Could not delete expense.");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-white">My Expenses</h2>
          <p className="text-sm text-slate-400">Track, draft, and submit reimbursement claims</p>
        </div>
        <button
          onClick={() => {
            setEditingExpense(null);
            setModalOpen(true);
          }}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg cursor-pointer transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>New Expense</span>
        </button>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-slate-950/60 text-xs uppercase text-slate-400 border-b border-slate-800">
            <tr>
              <th className="px-6 py-3.5">Title</th>
              <th className="px-6 py-3.5">Category</th>
              <th className="px-6 py-3.5">Amount</th>
              <th className="px-6 py-3.5">Status</th>
              <th className="px-6 py-3.5 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {loading ? (
              <tr>
                <td colSpan="5" className="px-6 py-8 text-center text-slate-500">
                  Loading expenses...
                </td>
              </tr>
            ) : expenses.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-8 text-center text-slate-500">
                  No expenses found. Click "New Expense" to start a draft.
                </td>
              </tr>
            ) : (
              expenses.map((item) => (
                <tr key={item.id} className="hover:bg-slate-800/30">
                  <td className="px-6 py-4 font-medium text-white">{item.title}</td>
                  <td className="px-6 py-4 text-slate-400">{item.category}</td>
                  <td className="px-6 py-4 font-mono font-semibold text-slate-200">
                    ${parseFloat(item.amount).toFixed(2)}
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={item.status} />
                  </td>
                  <td className="px-6 py-4 text-right space-x-2">
                    {item.status === "DRAFT" && (
                      <>
                        <button
                          onClick={() => {
                            setEditingExpense(item);
                            setModalOpen(true);
                          }}
                          className="p-1.5 text-slate-400 hover:text-indigo-400 cursor-pointer"
                          title="Edit Draft"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(item.id)}
                          className="p-1.5 text-slate-400 hover:text-rose-400 cursor-pointer"
                          title="Delete Draft"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleSubmitExpense(item.id)}
                          className="p-1.5 text-slate-400 hover:text-emerald-400 cursor-pointer"
                          title="Submit for Approval"
                        >
                          <Send className="w-4 h-4" />
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <ExpenseModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSave={handleSave}
        initialData={editingExpense}
      />
    </div>
  );
}