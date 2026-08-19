import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

const ROLE_TABS = {
  store_manager: ['dashboard', 'recommendations', 'heatmap'],
  retail_analyst: ['dashboard', 'segments', 'scores', 'heatmap'],
  marketing_manager: ['dashboard', 'scores', 'recommendations'],
  admin: ['dashboard', 'segments', 'scores', 'recommendations', 'heatmap'],
};

const TAB_LABELS = {
  dashboard: '📊 Analytics',
  segments: '👥 Segments',
  scores: '⭐ Scores',
  recommendations: '💡 Recommendations',
  heatmap: '🗺️ Heatmap',
};

function App() {
  const [token, setToken] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [analyticsData, setAnalyticsData] = useState(null);
  const [segments, setSegments] = useState(null);
  const [scores, setScores] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [heatmap, setHeatmap] = useState(null);
  const [heatmapLoading, setHeatmapLoading] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('dashboard');
  const [userRole, setUserRole] = useState(null);

  const handleLogin = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const data = await response.json();
      if (data.access_token) {
        setToken(data.access_token);
        setIsLoggedIn(true);
        setError('');
      } else {
        setError('Invalid credentials');
      }
    } catch (err) {
      setError('Connection error');
    }
  };

  const fetchData = async (endpoint, setter) => {
    try {
      const response = await fetch(`http://localhost:8000${endpoint}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const data = await response.json();
      setter(data);
    } catch (err) {
      console.error(`Failed to fetch ${endpoint}`);
    }
  };

  const fetchHeatmap = async () => {
    setHeatmapLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/intelligence/heatmap', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const data = await response.json();
      // handle both string and object responses
      if (typeof data === 'string') {
        setHeatmap(data);
      } else if (data.heatmap) {
        setHeatmap(data.heatmap);
      } else {
        setHeatmap(null);
      }
    } catch (err) {
      console.error('Failed to fetch heatmap');
      setHeatmap(null);
    } finally {
      setHeatmapLoading(false);
    }
  };

  useEffect(() => {
    if (isLoggedIn) {
      fetch('http://localhost:8000/api/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` },
      })
        .then((res) => res.json())
        .then((data) => {
          const role = data.role || 'admin';
          setUserRole(role);
          const allowedTabs = ROLE_TABS[role] || ROLE_TABS.admin;
          setActiveTab(allowedTabs[0]);
        })
        .catch(() => setUserRole('admin'));

      fetchData('/api/analytics/attention', setAnalyticsData);
      fetchData('/api/intelligence/segments', setSegments);
      fetchData('/api/intelligence/scores', setScores);
      fetchData('/api/intelligence/recommendations', setRecommendations);
    }
  }, [isLoggedIn, token]);

  // Load heatmap only when heatmap tab is clicked
  useEffect(() => {
    if (activeTab === 'heatmap' && isLoggedIn && !heatmap) {
      fetchHeatmap();
    }
  }, [activeTab]);

  if (!isLoggedIn) {
    return (
      <div className="login-container">
        <h1>Consumer Attention Mapping System</h1>
        <div className="login-box">
          <h2>Login</h2>
          <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <button onClick={handleLogin}>Login</button>
          {error && <p className="error">{error}</p>}
        </div>
      </div>
    );
  }

  const allowedTabs = ROLE_TABS[userRole] || ROLE_TABS.admin;

  return (
    <div className="dashboard">
      <h1>🛍️ Consumer Attention Dashboard</h1>
      {userRole && <p className="role-label">Logged in as: <strong>{userRole.replace('_', ' ')}</strong></p>}

      <div className="tabs">
        {allowedTabs.map((tab) => (
          <button
            key={tab}
            className={activeTab === tab ? 'active' : ''}
            onClick={() => setActiveTab(tab)}
          >
            {TAB_LABELS[tab]}
          </button>
        ))}
      </div>

      {activeTab === 'dashboard' && analyticsData && (
        <div>
          <div className="stats-row">
            <div className="stat-card"><h3>Total Shoppers Today</h3><p>{analyticsData.total_shoppers_today}</p></div>
            <div className="stat-card"><h3>Average Dwell Time</h3><p>{analyticsData.average_dwell_time}s</p></div>
            <div className="stat-card"><h3>Most Viewed Shelf</h3><p>{analyticsData.most_viewed_shelf}</p></div>
          </div>
          <div className="chart-container">
            <h2>Shelf Attention Analytics</h2>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={analyticsData.shelves}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="shelf" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="dwell_time" fill="#8884d8" name="Dwell Time (seconds)" />
                <Bar dataKey="shoppers" fill="#82ca9d" name="Number of Shoppers" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {activeTab === 'segments' && segments && (
        <div className="chart-container">
          <h2>Shopper Behavior Segments</h2>
          <table className="data-table">
            <thead><tr><th>Shopper ID</th><th>Segment</th><th>Description</th><th>Dwell Time</th></tr></thead>
            <tbody>
              {segments.segments.map((s, i) => (
                <tr key={i}>
                  <td>#{s.shopper_id}</td>
                  <td><span className="badge">{s.segment}</span></td>
                  <td>{s.description}</td>
                  <td>{s.dwell_time}s</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'scores' && scores && (
        <div className="chart-container">
          <h2>Product Attractiveness Scores</h2>
          <table className="data-table">
            <thead><tr><th>Product</th><th>Score</th><th>Rating</th></tr></thead>
            <tbody>
              {scores.products.map((p, i) => (
                <tr key={i}>
                  <td>{p.product}</td>
                  <td>{p.score}</td>
                  <td><span className={`badge ${p.rating.toLowerCase()}`}>{p.rating}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'recommendations' && recommendations && (
        <div className="chart-container">
          <h2>Product Recommendations</h2>
          {recommendations.recommendations.map((r, i) => (
            <div key={i} className={`recommendation ${r.priority.toLowerCase()}`}>
              <h3>{r.product} — {r.issue}</h3>
              <p>{r.recommendation}</p>
              <span className="priority">Priority: {r.priority}</span>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'heatmap' && (
        <div className="chart-container">
          <h2>Store Attention Heatmap</h2>
          {heatmapLoading && <p>⏳ Processing video, please wait...</p>}
          {!heatmapLoading && heatmap && (
            <img
              src={heatmap}
              alt="Store Heatmap"
              style={{ width: '100%', borderRadius: '8px' }}
            />
          )}
          {!heatmapLoading && !heatmap && (
            <div>
              <p>Heatmap not loaded yet.</p>
              <button onClick={fetchHeatmap}>🔄 Generate Heatmap</button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;