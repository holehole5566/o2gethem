import React, { useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { login } from "../services/api";
import { setLoggedIn } from "../store/authSlice";
import type { RootState, AppDispatch } from "../store";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [msg, setMsg] = useState("");
  const { isLoggedIn } = useSelector((state: RootState) => state.auth);
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const data = await login(username, password);
      if (data.status === "ok"){
          setMsg("Login successful!");
          dispatch(setLoggedIn(true));
          setTimeout(() => {
            navigate("/profile");
          }, 1000);
      } else {
          setMsg(data.message || "Invalid credentials");
      }
    } catch (err: any) {
      console.log(err);
      if (err.status === 401) {
        setMsg("Invalid username or password");
      } else if (err.status === 400) {
        setMsg("Please enter username and password");
      } else {
        setMsg("Login failed. Please try again.");
      }
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
          <button type="submit">Login</button>
        </form>
      ) : (
        <div className="form">
          <p>You are successfully logged in!</p>
        </div>
      )}
      {msg && <div className={`message ${isLoggedIn ? 'success' : 'error'}`}>{msg}</div>}
    </div>
  );
}