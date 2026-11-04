import React, { useState, useEffect } from "react";
import { Check, X, MessageSquare } from "lucide-react";
import { fetchExpenses, reviewExpense } from "../api/endpoints";
import StatusBadge from "./StatusBadge";

export default function ManagerQueue() {
  const [pending, setPending] = useState([]);
  const [loading, setLoading] = useState(true);
  const [commentModal, setCommentModal] = useState({ open: false, id: null, action: null });
  const [comment, setComment] = useState("");

  const loadPending = async () => {
    try {
      setLoading(true);
      // Fetch only SUBMITTED items for the approval queue
      const res = await fetchExpenses({ status: "SUBMITTED" });
      setPending(res.data);
    } catch (err) {
      console.error("Failed to load queue:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPending();
  }, []);

 const handleReviewAction = async () => {
    const { id, action } = commentModal;
    const trimmed = comment.trim();

    // Frontend pre-check for REJECT
    if (action === "REJECT" && !trimmed) {
      alert("A rejection reason is required when rejecting an expense.");
      return;
    }

    try {
      await reviewExpense(id, {
        action: action, // "APPROVE" or "REJECT"
        comment: trimmed || null,
        rejection_reason: action === "REJECT" ? trimmed : null,
      });

      setCommentModal({ open: false, id: null, action: null });
      setComment("");
      loadPending();
    } catch (err) {
      const detail = err.response?.data?.detail;
      const message = Array.isArray(detail)
        ? detail.map((d) => `${d.loc?.slice(-1)}: ${d.msg}`).join(", ")
        : typeof detail === "object"
        ? JSON.stringify(detail)
        : detail || "Review action failed.";
      alert(message);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-white">Manager Approval Queue</h2>
        <p className="text-sm text-slate-400">Review, approve, or reject employee submissions</p>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-slate-950/60 text-xs uppercase text-slate-400 border-b border-slate-800">
            <tr>
              <th className="px-6 py-3.5">Title</th>
              <th className="px-6 py-3.5">Category</th>
              <th className="px-6 py-3.5">Amount</th>
              <th className="px-6 py-3.5">Status</th>
              <th className="px-6 py-3.5 text-right">Review Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {loading ? (
              <tr>
                <td colSpan="5" className="px-6 py-8 text-center text-slate-500">
                  Loading approval queue...
                </td>
              </tr>
            ) : pending.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-8 text-center text-slate-500">
                  No submissions pending review.
                </td>
              </tr>
            ) : (
              pending.map((item) => (
                <tr key={item.id} className="hover:bg-slate-800/30">
                  <td className="px-6 py-4">
                    <div className="font-medium text-white">{item.title}</div>
                    {item.description && (
                      <div className="text-xs text-slate-400 mt-0.5">{item.description}</div>
                    )}
                  </td>
                  <td className="px-6 py-4 text-slate-400">{item.category}</td>
                  <td className="px-6 py-4 font-mono font-semibold text-slate-200">
                    ${parseFloat(item.amount).toFixed(2)}
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={item.status} />
                  </td>
                  <td className="px-6 py-4 text-right space-x-2">
                    <button
                      onClick={() => setCommentModal({ open: true, id: item.id, action: "APPROVE" })}
                      className="inline-flex items-center gap-1 px-3 py-1.5 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-300 border border-emerald-600/30 text-xs font-medium rounded-lg cursor-pointer transition-colors"
                    >
                      <Check className="w-3.5 h-3.5" /> Approve
                    </button>
                    <button
                      onClick={() => setCommentModal({ open: true, id: item.id, action: "REJECT" })}
                      className="inline-flex items-center gap-1 px-3 py-1.5 bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-600/30 text-xs font-medium rounded-lg cursor-pointer transition-colors"
                    >
                      <X className="w-3.5 h-3.5" /> Reject
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {commentModal.open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-md w-full p-6 shadow-2xl">
            <h3 className="text-lg font-semibold text-white mb-2">
              {commentModal.action === "APPROVE" ? "Approve Expense" : "Reject Expense"}
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Add optional feedback or reason for this audit decision.
            </p>
            <textarea
              rows="3"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-white text-sm focus:outline-none focus:border-indigo-500 mb-4"
              placeholder="e.g. Budget confirmed / Missing receipt..."
            />
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setCommentModal({ open: false, id: null, action: null })}
                className="px-4 py-2 text-sm text-slate-300 hover:text-white"
              >
                Cancel
              </button>
              <button
                onClick={handleReviewAction}
                className={`px-4 py-2 text-white text-sm font-medium rounded-lg transition-colors cursor-pointer ${
                  commentModal.action === "APPROVE"
                    ? "bg-emerald-600 hover:bg-emerald-500"
                    : "bg-rose-600 hover:bg-rose-500"
                }`}
              >
                Confirm {commentModal.action === "APPROVE" ? "Approval" : "Rejection"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}