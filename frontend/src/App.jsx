import React from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Login from "./components/Login";

function MainApp() {
  const { user, logout } = useAuth();

  if (!user) {
    return <Login />;
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8">
      <div className="max-w-5xl mx-auto flex justify-between items-center pb-6 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-bold">Expense Approval Dashboard</h1>
          <p className="text-sm text-slate-400">
            Logged in as <span className="font-semibold text-indigo-400">{user.username}</span> ({user.role})
          </p>
        </div>
        <button
          onClick={logout}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-sm font-medium rounded-lg text-slate-200 transition-colors"
        >
          Sign Out
        </button>
      </div>
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