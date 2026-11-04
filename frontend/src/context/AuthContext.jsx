import React, { createContext, useContext, useState, useEffect } from "react";
import { loginUser, fetchCurrentUser } from "../api/endpoints";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("user");
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem("token");
      if (token) {
        try {
          const res = await fetchCurrentUser();
          setUser(res.data);
          localStorage.setItem("user", JSON.stringify(res.data));
        } catch {
          localStorage.removeItem("token");
          localStorage.removeItem("user");
          setUser(null);
        }
      }
      setLoading(false);
    };
    initAuth();
  }, []);

  const login = async (username, password) => {
    const res = await loginUser(username, password);
    const token = res.data.access_token;
    localStorage.setItem("token", token);

    const userRes = await fetchCurrentUser();
    setUser(userRes.data);
    localStorage.setItem("user", JSON.stringify(userRes.data));
    return userRes.data;
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);