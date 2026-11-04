import React, { useState } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Login from "./components/Login";
import EmployeeDashboard from "./components/EmployeeDashboard";
import ManagerQueue from "./components/ManagerQueue";
import { LogOut, FileText, CheckSquare } from "lucide-react";

function MainApp() {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState("expenses");

  if (!user) {
    return <Login />;
  }

  const isManagerOrAdmin = user.role === "MANAGER" || user.role === "ADMIN";

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Navigation Bar */}
      <header className="border-b border-slate-800 bg-slate-900/60 sticky top-0 z-40 backdrop-blur">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <span className="font-bold text-lg text-indigo-400">ExpenseFlow</span>
            <nav className="flex gap-2">
              <button
                onClick={() => setActiveTab("expenses")}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors cursor-pointer ${
                  activeTab === "expenses"
                    ? "bg-indigo-600 text-white"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                <FileText className="w-4 h-4" /> My Expenses
              </button>
              {isManagerOrAdmin && (
                <button
                  onClick={() => setActiveTab("queue")}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors cursor-pointer ${
                    activeTab === "queue"
                      ? "bg-indigo-600 text-white"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <CheckSquare className="w-4 h-4" /> Approval Queue
                </button>
              )}
            </nav>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-xs font-semibold text-white">{user.username}</div>
              <div className="text-[10px] text-indigo-400 uppercase tracking-wider">{user.role}</div>
            </div>
            <button
              onClick={logout}
              className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors cursor-pointer"
              title="Sign Out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        {activeTab === "expenses" ? <EmployeeDashboard /> : <ManagerQueue />}
      </main>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}