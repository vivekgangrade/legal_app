import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor to handle errors (e.g., 401)
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export const login = async (username, password) => {
    // Use URLSearchParams for OAuth2 compatibility if backend expects form data
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);

    // Note: /users/token usually expects form-data for OAuth2 in FastAPI
    const response = await api.post('/users/token', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });
    return response.data;
};

export const getCases = async () => {
    const response = await api.get('/cases');
    return response.data;
};

export const createCase = async (caseData) => {
    const response = await api.post('/cases', caseData);
    return response.data;
};

export default api;
