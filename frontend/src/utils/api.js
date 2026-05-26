import axios from 'axios'

const protocol = window.location.protocol
const hostname = window.location.hostname
const baseURL = `${protocol}//${hostname}:8081/api`

console.log(`API base URL: ${baseURL}`)

const instance = axios.create({
  baseURL: baseURL,
  timeout: 10000,
})

instance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

export const authAPI = {
  login: (data) => instance.post('/auth/login', data),
  register: (data) => instance.post('/auth/register', data),
  profile: () => instance.get('/auth/profile'),
  adminLogin: (data) => instance.post('/auth/admin/login', data),
}

export const testAPI = {
  start: (data) => instance.post('/test/start', data),
  startSmart: (data) => instance.post('/test/start/smart', data),
  startStandard: (data) => instance.post('/test/start/standard', data),
  submit: (data) => instance.post('/test/submit', data),
  records: () => instance.get('/test/records'),
  record: (id) => instance.get(`/test/record/${id}`),
}

export const userAPI = {
  stats: () => instance.get('/user/stats'),
  wrongWords: () => instance.get('/user/wrong_words'),
  removeWrongWord: (id) => instance.delete(`/user/wrong_words/${id}`),
}

export const vocabAPI = {
  list: (params) => instance.get('/vocab/search', { params }),
  add: (data) => instance.post('/vocab/add', data),
  update: (id, data) => instance.put(`/vocab/${id}`, data),
  delete: (id) => instance.delete(`/vocab/${id}`),
  batchDelete: (ids) => instance.post('/vocab/batch-delete', { ids }),
  upload: (formData) => instance.post('/vocab/upload', formData, { timeout: 30000 }),
  importParsed: (data) => instance.post('/vocab/import-parsed', data),
}

export const adminAPI = {
  stats: () => instance.get('/admin/stats'),
  users: (params) => instance.get('/admin/users', { params }),
  deleteUser: (id) => instance.delete(`/admin/users/${id}`),
}

export default instance
