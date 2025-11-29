import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [projects, setProjects] = useState([]);
  const [currentProject, setCurrentProject] = useState(null);

  const login = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post(`${API_URL}/login`, { phone, password });
      setToken(res.data.access_token);
      localStorage.setItem('token', res.data.access_token);
      alert('ورود موفق!');
    } catch (err) {
      alert('خطا در ورود: ' + (err.response?.data?.detail || err.message));
    }
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem('token');
  };

  const loadProjects = async () => {
    try {
      const res = await axios.get(`${API_URL}/projects`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProjects(res.data);
    } catch (err) {
      alert('خطا در بارگذاری پروژه‌ها');
    }
  };

  if (!token) {
    return (
      <div className="container">
        <div className="login-box">
          <h1>🎯 سیستم AHP حیات</h1>
          <form onSubmit={login}>
            <input
              type="text"
              placeholder="شماره موبایل"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="رمز عبور"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button type="submit">ورود</button>
          </form>
          <p className="hint">
            💡 ادمین: 09123456789 / Admin@Hayat2025
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="header">
        <h1>📊 داشبورد AHP</h1>
        <button onClick={logout} className="logout-btn">خروج</button>
      </div>
      <div className="dashboard">
        <button onClick={loadProjects} className="load-btn">
          🔄 بارگذاری پروژه‌ها
        </button>
        <div className="projects-list">
          <h2>پروژه‌های من ({projects.length})</h2>
          {projects.map(p => (
            <div key={p.id} className="project-item">
              <h3>{p.title}</h3>
              <p>{p.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default App;
