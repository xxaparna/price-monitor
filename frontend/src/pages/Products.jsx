import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getProducts } from '../api'

export default function Products() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [filters, setFilters] = useState({
    source:'', brand:'', min_price:'', max_price:'', sort_by:'updated_at', order:'desc'
  })

  const fetchProducts = (p = 1, f = filters) => {
    setLoading(true)
    const params = { page: p, page_size: 20 }
    if (f.source) params.source = f.source
    if (f.brand) params.brand = f.brand
    if (f.min_price) params.min_price = f.min_price
    if (f.max_price) params.max_price = f.max_price
    params.sort_by = f.sort_by
    params.order = f.order
    getProducts(params)
      .then(r => setProducts(r.data))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchProducts(1) }, [])

  const handleFilter = () => { setPage(1); fetchProducts(1, filters) }
  const handlePage = (p) => { setPage(p); fetchProducts(p) }

  return (
    <div className="page">
      <h1 style={{ fontSize:'1.4rem', marginBottom:'1.5rem' }}>Products</h1>

      <div className="filters">
        <select value={filters.source} onChange={e => setFilters({...filters, source: e.target.value})}>
          <option value="">All sources</option>
          <option value="grailed">Grailed</option>
          <option value="fashionphile">Fashionphile</option>
          <option value="1stdibs">1stdibs</option>
        </select>
        <input
          placeholder="Brand"
          value={filters.brand}
          onChange={e => setFilters({...filters, brand: e.target.value})}
        />
        <input
          placeholder="Min price"
          type="number"
          value={filters.min_price}
          onChange={e => setFilters({...filters, min_price: e.target.value})}
          style={{ width:'110px' }}
        />
        <input
          placeholder="Max price"
          type="number"
          value={filters.max_price}
          onChange={e => setFilters({...filters, max_price: e.target.value})}
          style={{ width:'110px' }}
        />
        <select value={filters.sort_by} onChange={e => setFilters({...filters, sort_by: e.target.value})}>
          <option value="updated_at">Latest</option>
          <option value="current_price">Price</option>
          <option value="brand">Brand</option>
        </select>
        <select value={filters.order} onChange={e => setFilters({...filters, order: e.target.value})}>
          <option value="desc">Desc</option>
          <option value="asc">Asc</option>
        </select>
        <button
          onClick={handleFilter}
          style={{
            padding:'0.5rem 1.2rem',
            background:'#1a1a2e',
            color:'#fff',
            border:'none',
            borderRadius:'6px',
            cursor:'pointer',
          }}
        >
          Apply
        </button>
      </div>

      {loading ? (
        <div className="loading">Loading products...</div>
      ) : (
        <>
          <div className="product-grid">
            {products.map(p => (
              <Link to={`/products/${p.id}`} className="product-card" key={p.id}>
                <img
                  src={p.image_url || ''}
                  alt={p.model}
                  onError={e => { e.target.style.display='none' }}
                />
                <div className="info">
                  <div className="brand">{p.brand}</div>
                  <div className="model">{p.model}</div>
                  <div className="price">
                    {p.current_price ? `$${p.current_price.toLocaleString()}` : 'N/A'}
                  </div>
                  <span className={`badge badge-${p.source}`}>{p.source}</span>
                  {p.is_sold && <span className="badge badge-sold" style={{ marginLeft:'0.4rem' }}>Sold</span>}
                </div>
              </Link>
            ))}
          </div>

          <div className="pagination">
            <button onClick={() => handlePage(page - 1)} disabled={page === 1}>← Prev</button>
            <button className="active">{page}</button>
            <button onClick={() => handlePage(page + 1)} disabled={products.length < 20}>Next →</button>
          </div>
        </>
      )}
    </div>
  )
}