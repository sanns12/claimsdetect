import API from './api';

export const login = async (email, password, role) => {
  try {
    console.log('📤 Sending login request to backend...');
    console.log('URL:', '/auth/login');
    console.log('Data:', { email, role });
    
    const response = await API.post('/auth/login', {
      email,
      password,
      role: role.toLowerCase()
    });
    
    console.log('📥 Login response received:', response.status);
    console.log('Response data:', response.data);
    
    if (response.data.token) {
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      localStorage.setItem('role', role);
      sessionStorage.setItem('authenticated', 'true');
      console.log('✅ Login successful, token stored');
    }
    
    return response.data;
  } catch (error) {
    console.error('❌ Login error details:');
    
    if (error.response) {
      // Server responded with error
      console.error('Status:', error.response.status);
      console.error('Data:', error.response.data);
      console.error('Headers:', error.response.headers);
      
      // Clear any stale auth data
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      localStorage.removeItem('role');
      sessionStorage.removeItem('authenticated');
      
      throw error.response.data || { message: `Login failed (${error.response.status})` };
    } else if (error.request) {
      // Request made but no response
      console.error('No response received from server');
      console.error('Request:', error.request);
      throw { message: 'Cannot connect to server. Make sure backend is running.' };
    } else {
      // Something else
      console.error('Error:', error.message);
      throw { message: error.message || 'Login failed' };
    }
  }
};

export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  localStorage.removeItem('role');
  sessionStorage.removeItem('authenticated');
};

export const getCurrentUser = () => {
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

export const getCurrentRole = () => {
  return localStorage.getItem('role');
};

export const isAuthenticated = () => {
  return !!localStorage.getItem('token');
};