// src/components/AuthForm.jsx
import { useState } from "react";
import { login, signup } from "../api/auth.api";

export default function AuthForm({ onAuthenticated }) {
  const [mode, setMode] = useState("login"); // "login" | "signup"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);

    try {
      if (mode === "signup") {
        const signupRes = await signup(email, fullName, password);
        if (!signupRes) {
          throw new Error("Signup failed");
        }
      }

      // Whether just signed up or logging in directly, log in now
      const loginRes = await login(email, password);
      if (!loginRes) {
        throw new Error("Login failed");
      }

      onAuthenticated();
    } catch (err) {
      console.error(err);
      setError(
        mode === "signup"
          ? "Signup failed. Email may already be registered."
          : "Invalid email or password."
      );
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth-form">
      <h2>{mode === "login" ? "Log In" : "Sign Up"}</h2>

      <form onSubmit={handleSubmit}>
        {mode === "signup" && (
          <input
            type="text"
            placeholder="Full name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
          />
        )}

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button type="submit" disabled={busy}>
          {busy ? "Please wait…" : mode === "login" ? "Log In" : "Sign Up"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      <p>
        {mode === "login" ? "Don't have an account?" : "Already have an account?"}{" "}
        <button
          type="button"
          className="link-button"
          onClick={() => {
            setMode(mode === "login" ? "signup" : "login");
            setError("");
          }}
        >
          {mode === "login" ? "Sign up" : "Log in"}
        </button>
      </p>
    </div>
  );
}