import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getProduct } from '../api'
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid
} from 'recharts'

export default function ProductDetail() {
  const { id } = useParams()
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getProduct(id)
      .then(r => setProduct(r.data))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="loading">Loading product...</div>
  if (!product) return <div className="error">Product not found.</div>

  const chartData = product.price_history.map(h => ({
    date: new Date(h.recorded_at).toLocaleDateString(),
    price: h.price,
  }))

  return (
    <div className="page">
      <Link to="/products" className="back-btn">Back to products</Link>

      <div className="detail-header">
        {product.image_url && (
          <img src={product.image_url} alt={product.model} />
        )}
        <div className="detail-info">
          <span className={`badge badge-${product.source}`}>{product.source}</span>
          <h1 style={{ marginTop:'0.75rem' }}>{product.model}</h1>
          <div className="price-big">
            {product.current_price ? `$${product.current_price.toLocaleString()}` : 'N/A'}
          </div>
          <p><strong>Brand:</strong> {product.brand}</p>
          <p><strong>Category:</strong> {product.category}</p>
          {product.condition && (
            <p><strong>Condition:</strong> {product.condition}</p>
          )}
          {product.seller_location && (
            <p><strong>Location:</strong> {product.seller_location}</p>
          )}
          <p><strong>Status:</strong> {product.is_sold ? 'Sold' : 'Available'}</p>
          {product.product_url && (
            <a
              href={product.product_url}
              target="_blank"
              rel="noreferrer"
              style={{ display:'inline-block', marginTop:'1rem', color:'#1a1a2e', fontSize:'0.9rem' }}
            >
              View on {product.source}
            </a>
          )}
        </div>
      </div>

      {product.description && (
        <div className="card">
          <h2>Description</h2>
          <p style={{ fontSize:'0.9rem', color:'#555', lineHeight:1.6 }}>
            {product.description}
          </p>
        </div>
      )}

      {chartData.length > 1 && (
        <div className="card">
          <h2>Price history chart</h2>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" fontSize={12} />
              <YAxis fontSize={12} tickFormatter={v => `$${v.toLocaleString()}`} />
              <Tooltip formatter={v => `$${v.toLocaleString()}`} />
              <Line
                type="monotone"
                dataKey="price"
                stroke="#1a1a2e"
                strokeWidth={2}
                dot={{ r:4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="card">
        <h2>Price history log</h2>
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Price</th>
              <th>Change</th>
            </tr>
          </thead>
          <tbody>
            {product.price_history.length === 0 ? (
              <tr>
                <td colSpan={3} style={{ color:'#888' }}>No history yet</td>
              </tr>
            ) : (
              product.price_history.map(h => (
                <tr key={h.id}>
                  <td>{new Date(h.recorded_at).toLocaleString()}</td>
                  <td>${h.price.toLocaleString()}</td>
                  <td>
                    {h.price_delta === 0 || h.price_delta === null ? (
                      <span style={{ color:'#888' }}>Initial</span>
                    ) : h.price_delta > 0 ? (
                      <span className="positive">+${h.price_delta}</span>
                    ) : (
                      <span className="negative">-${Math.abs(h.price_delta)}</span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
