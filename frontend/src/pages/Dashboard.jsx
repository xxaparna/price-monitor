import { useEffect, useState } from 'react'
import { getAnalytics, triggerRefresh } from '../api'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid
} from 'recharts'

export default function Dashboard() {
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [refreshResult, setRefreshResult] = useState(null)

  useEffect(() => {
    getAnalytics()
      .then(r => setAnalytics(r.data))
      .finally(() => setLoading(false))
  }, [])

  const handleRefresh = async () => {
    setRefreshing(true)
    setRefreshResult(null)
    try {
      const r = await triggerRefresh()
      setRefreshResult(r.data)
      const updated = await getAnalytics()
      setAnalytics(updated.data)
    } finally {
      setRefreshing(false)
    }
  }

if (loading) return <div className="loading">Loading dashboard...</div>
if (!analytics) return <div className="error">Failed to load analytics. Check API connection.</div>

  return (
    <div className="page">
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'1.5rem' }}>
        <h1 style={{ fontSize:'1.4rem' }}>Dashboard</h1>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          style={{
            padding:'0.6rem 1.2rem',
            background:'#1a1a2e',
            color:'#fff',
            border:'none',
            borderRadius:'6px',
            cursor: refreshing ? 'not-allowed' : 'pointer',
            opacity: refreshing ? 0.7 : 1,
          }}
        >
          {refreshing ? 'Refreshing...' : '🔄 Refresh Data'}
        </button>
      </div>

      {refreshResult && (
        <div className="card" style={{ background:'#f0fff4', marginBottom:'1rem' }}>
          <p style={{ color:'#1a6b3a', fontSize:'0.9rem' }}>
            ✅ Refresh complete — Processed: {refreshResult.total_processed} |
            New: {refreshResult.total_new} |
            Updated: {refreshResult.total_updated} |
            Errors: {refreshResult.total_errors}
          </p>
        </div>
      )}

      <div className="stat-grid">
        <div className="stat-card">
          <h3>Total Products</h3>
          <div className="value">{analytics.total_products}</div>
        </div>
        <div className="stat-card">
          <h3>Sources</h3>
          <div className="value">{analytics.total_sources}</div>
        </div>
        {analytics.by_source.map(s => (
          <div className="stat-card" key={s.source}>
            <h3>{s.source}</h3>
            <div className="value">{s.total_products}</div>
            <div style={{ fontSize:'0.85rem', color:'#888', marginTop:'0.25rem' }}>
              Avg ${s.avg_price?.toLocaleString()}
            </div>
          </div>
        ))}
      </div>

      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'1.5rem' }}>
        <div className="card">
          <h2>Products by source</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={analytics.by_source}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="source" fontSize={12} />
              <YAxis fontSize={12} />
              <Tooltip />
              <Bar dataKey="total_products" fill="#1a1a2e" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h2>Avg price by source (USD)</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={analytics.by_source}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="source" fontSize={12} />
              <YAxis fontSize={12} />
              <Tooltip formatter={(v) => `$${v?.toLocaleString()}`} />
              <Bar dataKey="avg_price" fill="#6c63ff" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card" style={{ marginTop:'1.5rem' }}>
        <h2>By category</h2>
        <table>
          <thead>
            <tr>
              <th>Category</th>
              <th>Products</th>
              <th>Avg Price</th>
            </tr>
          </thead>
          <tbody>
            {analytics.by_category.map(c => (
              <tr key={c.category}>
                <td>{c.category}</td>
                <td>{c.total_products}</td>
                <td>{c.avg_price ? `$${c.avg_price.toLocaleString()}` : '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}