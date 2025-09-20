// Main entry point for the application

// Import global styles
import './styles/global.css';

// Initialize the application based on the current page
document.addEventListener('DOMContentLoaded', () => {
  const currentPath = window.location.pathname;
  
  // Route to appropriate module based on path
  if (currentPath.includes('login') || currentPath === '/' || currentPath === '') {
    import('./components/login/login.js');
  } else if (currentPath.includes('attendance')) {
    import('./components/attendance/attendance.js');
  } else if (currentPath.includes('reports')) {
    import('./components/reports/reports.js');
  } else if (currentPath.includes('students')) {
    import('./components/students/Manage-students.js');
  } else if (currentPath.includes('teacher')) {
    import('./components/teacher/teacher.js');
  }
});

// API Service for backend communication
export const ApiService = {
  baseUrl: 'http://localhost:8000/api',
  
  // Helper method for making API requests
  async request(endpoint, method = 'GET', data = null, token = null) {
    const url = `${this.baseUrl}${endpoint}`;
    
    const headers = {
      'Content-Type': 'application/json'
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const options = {
      method,
      headers,
      credentials: 'include'
    };
    
    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
      options.body = JSON.stringify(data);
    }
    
    try {
      const response = await fetch(url, options);
      
      // Handle non-JSON responses
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const result = await response.json();
        
        if (!response.ok) {
          throw new Error(result.detail || 'API request failed');
        }
        
        return result;
      } else {
        if (!response.ok) {
          throw new Error('API request failed');
        }
        return await response.text();
      }
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  },
  
  // Authentication methods
  auth: {
    login: (email, password, role) => ApiService.request('/auth/login', 'POST', { email, password, role }),
    register: (name, email, password, role) => ApiService.request('/auth/register', 'POST', { name, email, password, role }),
    getCurrentUser: () => {
      const token = localStorage.getItem('token');
      return token ? ApiService.request('/auth/me', 'GET', null, token) : null;
    }
  },
  
  // Attendance methods
  attendance: {
    mark: (imageFile, location) => {
      const formData = new FormData();
      formData.append('file', imageFile);
      if (location) formData.append('location', location);
      
      const token = localStorage.getItem('token');
      return ApiService.request('/attendance/mark', 'POST', formData, token);
    },
    getHistory: (userId, startDate, endDate) => {
      const token = localStorage.getItem('token');
      let endpoint = `/attendance/history/${userId}`;
      
      if (startDate || endDate) {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        endpoint += `?${params.toString()}`;
      }
      
      return ApiService.request(endpoint, 'GET', null, token);
    }
  },
  
  // User methods
  users: {
    getAll: () => {
      const token = localStorage.getItem('token');
      return ApiService.request('/users', 'GET', null, token);
    },
    getById: (id) => {
      const token = localStorage.getItem('token');
      return ApiService.request(`/users/${id}`, 'GET', null, token);
    }
  }
};

// Auth utilities
export const AuthService = {
  setToken: (token) => {
    localStorage.setItem('token', token);
  },
  
  getToken: () => {
    return localStorage.getItem('token');
  },
  
  removeToken: () => {
    localStorage.removeItem('token');
  },
  
  setUser: (user) => {
    localStorage.setItem('user', JSON.stringify(user));
  },
  
  getUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },
  
  removeUser: () => {
    localStorage.removeItem('user');
  },
  
  isAuthenticated: () => {
    return !!AuthService.getToken();
  },
  
  logout: () => {
    AuthService.removeToken();
    AuthService.removeUser();
    window.location.href = '/login.html';
  }
};
