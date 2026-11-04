import { api } from "./client";

// Auth
export const loginUser = async (username, password) => {
  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);
  return api.post("/auth/login", formData, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
};

export const fetchCurrentUser = () => api.get("/auth/me");

// Expenses
export const fetchExpenses = (params) => api.get("/expenses/", { params });
export const createExpense = (data) => api.post("/expenses/", data);
export const updateExpense = (id, data) => api.put(`/expenses/${id}`, data);
export const deleteExpense = (id) => api.delete(`/expenses/${id}`);
export const submitExpense = (id) => api.post(`/expenses/${id}/submit`);
export const reviewExpense = (id, data) => api.post(`/expenses/${id}/review`, data);