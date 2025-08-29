import React, { useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { login } from "../services/api";
import { setLoggedIn } from "../store/authSlice";
import { useApi } from "../hooks/useApi";
import type { RootState, AppDispatch } from "../store";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const { isLoggedIn } = useSelector((state: RootState) => state.auth);
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { execute, loading, error } = useApi();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const data = await execute(() => login(username, password));
      if (data.status === "ok") {
        dispatch(setLoggedIn(true));
        navigate("/profile");
      }
    } catch (err: any) {
      dispatch(setLoggedIn(false));
    }
  };


  return (
    <div className="page-container">
      <h2>{isLoggedIn ? "Welcome Back!" : "Sign In"}</h2>
      {!isLoggedIn ? (
        <form onSubmit={handleLogin} className="form">
          <input
            placeholder="Username"
            value={username}
            onChange={e => setUsername(e.target.value)}
          />
          <input
            placeholder="Password"
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
          />
          <button type="submit" disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
      ) : (
        <div className="form">
          <p>You are successfully logged in!</p>
        </div>
      )}
      {error && <div className="message error">{error}</div>}
      {isLoggedIn && <div className="message success">Login successful!</div>}
    </div>
  );
}