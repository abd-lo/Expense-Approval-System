import React from "react";

export default function StatusBadge({ status }) {
  const styles = {
    DRAFT: "bg-slate-800 text-slate-300 border-slate-700",
    SUBMITTED: "bg-amber-950/50 text-amber-300 border-amber-800/60",
    APPROVED: "bg-emerald-950/50 text-emerald-300 border-emerald-800/60",
    REJECTED: "bg-rose-950/50 text-rose-300 border-rose-800/60",
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${
        styles[status] || styles.DRAFT
      }`}
    >
      {status}
    </span>
  );
}