// src/api/auth.api.js
import { api, safe } from "./client";

const TOKEN_KEY = "access_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export async function login(email, password) {
  const res = await safe(() =>
    api.post("/api/v1/auth/login", { email, password })
  );
  if (!res?.data?.access_token) return null;
  setToken(res.data.access_token);
  return res.data;
}

export async function signup(email, fullName, password) {
  const res = await safe(() =>
    api.post("/api/v1/auth/signup", {
      email,
      full_name: fullName,
      password,
    })
  );
  return res?.data || null;
}