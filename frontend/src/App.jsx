import { useState } from "react";
import AuthForm from "./components/AuthForm";
import MainApp from "./MainApp";
import { getToken, clearToken } from "./api/auth.api";

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!getToken());
  const [sessionKey, setSessionKey] = useState(0);

  const handleLogout = () => {
    clearToken();
    setIsAuthenticated(false);
  };

  const handleAuthenticated = () => {
    setSessionKey((k) => k + 1); // forces a fresh MainApp instance
    setIsAuthenticated(true);
  };

  if (!isAuthenticated) {
    return <AuthForm onAuthenticated={handleAuthenticated} />;
  }

  return <MainApp key={sessionKey} onLogout={handleLogout} />;
}