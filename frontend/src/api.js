import axios from 'axios'

const API_KEY = 'admin-key-123'
const BASE_URL = 'http://127.0.0.1:8000'

const client = axios.create({
  baseURL: BASE_URL,
  headers: { 'X-API-Key': API_KEY },
})

export const getProducts = (params) => client.get('/products', { params })
export const getProduct = (id) => client.get(`/products/${id}`)
export const getAnalytics = () => client.get('/analytics')
export const triggerRefresh = () => client.post('/refresh')
export const getEvents = () => client.get('/events')
