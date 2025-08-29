import { useEffect, useState } from "react";
import { Routes, Route, Link, useNavigate } from "react-router-dom";
import { useSelector, useDispatch } from "react-redux";
import Register from "./pages/Register";
import Login from "./pages/Login";
import Profile from "./pages/Profile";
import Posts from "./pages/Posts";
import Dating from "./pages/Dating";
import Mailbox from "./pages/Mailbox";
import { logout as logoutApi } from "./services/api";
import { checkAuth, logout } from "./store/authSlice";
import type { RootState, AppDispatch } from "./store";
import "./App.css";

function App() {
  const { isLoggedIn } = useSelector((state: RootState) => state.auth);
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const [logoutMsg, setLogoutMsg] = useState("");

  useEffect(() => {
    dispatch(checkAuth());
  }, [dispatch]);

  const handleLogout = async () => {
    await logoutApi();
    dispatch(logout());
    setLogoutMsg("Logged out successfully!");
    setTimeout(() => {
      setLogoutMsg("");
      navigate("/");
    }, 1000);
  };

  return (
    <div className="app">
      <nav className="navbar">
        <Link to="/" className="nav-brand">O2geThem</Link>
        <div className="nav-links">
          <Link to="/register">Register</Link>
          {isLoggedIn ? (
            <button onClick={handleLogout} className="logout-btn">Logout</button>
          ) : (
            <Link to="/login">Login</Link>
          )}
          <Link to="/profile">Profile</Link>
          <Link to="/posts">Posts</Link>
          <Link to="/dating">Dating</Link>
          <Link to="/mailbox">Mailbox</Link>
        </div>
      </nav>
      <main className="main-content">
        {logoutMsg ? (
          <div className="page-container">
            <div className="message success">{logoutMsg}</div>
          </div>
        ) : (
          <Routes>
            <Route path="/" element={<div className="page-container"><h2>Welcome to O2geThem</h2><p>Please login or register to continue.</p></div>} />
            <Route path="/register" element={<Register />} />
            <Route path="/login" element={<Login />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/posts" element={<Posts />} />
            <Route path="/dating" element={<Dating />} />
            <Route path="/mailbox" element={<Mailbox />} />
          </Routes>
        )}
      </main>
    </div>
  );
}

export default App;
