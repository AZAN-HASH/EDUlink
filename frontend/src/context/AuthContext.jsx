import { createContext, startTransition, useContext, useEffect, useState } from "react";
import { authService } from "../services/authService";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("edulink_user");
    return stored ? JSON.parse(stored) : null;
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const accessToken = localStorage.getItem("edulink_access_token");
    if (!accessToken) {
      setLoading(false);
      return;
    }

    authService
      .getMe()
      .then((response) => {
        const currentUser = response.data.data;
        startTransition(() => {
          setUser(currentUser);
          localStorage.setItem("edulink_user", JSON.stringify(currentUser));
        });
      })
      .catch(() => {
        localStorage.removeItem("edulink_access_token");
        localStorage.removeItem("edulink_refresh_token");
        localStorage.removeItem("edulink_user");
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const persistAuth = (payload) => {
    const nextUser = payload.user;
    localStorage.setItem("edulink_access_token", payload.tokens.access_token);
    localStorage.setItem("edulink_refresh_token", payload.tokens.refresh_token);
    localStorage.setItem("edulink_user", JSON.stringify(nextUser));
    setUser(nextUser);
  };

  const login = async (credentials) => {
    const response = await authService.login(credentials);
    persistAuth(response.data.data);
    return response.data;
  };

  const register = async (payload) => {
    const response = await authService.register(payload);
    persistAuth(response.data.data);
    return response.data;
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (_error) {
      // Clear local auth even if the server token is already invalid.
    }
    localStorage.removeItem("edulink_access_token");
    localStorage.removeItem("edulink_refresh_token");
    localStorage.removeItem("edulink_user");
    setUser(null);
  };

  const refreshProfile = async () => {
    const response = await authService.getMe();
    const currentUser = response.data.data;
    setUser(currentUser);
    localStorage.setItem("edulink_user", JSON.stringify(currentUser));
    return currentUser;
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshProfile, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
