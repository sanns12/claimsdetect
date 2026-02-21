import API from './api';

// Get user dashboard stats
export const getUserDashboardStats = async () => {
  try {
    const response = await API.get('/dashboard/stats');
    return {
      total_claims: response.data.total_claims || 0,
      approved: response.data.approved || 0,
      flagged: response.data.flagged || 0,
      fraud: response.data.fraud || 0,
      pending_review: response.data.pending_review || 0,
      total_amount: response.data.total_amount || 0
    };
  } catch (error) {
    throw error.response?.data || { message: 'Failed to fetch dashboard stats' };
  }
};

// Get hospital dashboard stats
export const getHospitalDashboardStats = async () => {
  try {
    const response = await API.get('/dashboard/stats');
    return {
      total_claims: response.data.total_claims || 0,
      pending_review: response.data.pending_review || 0,
      approved: response.data.approved || 0,
      flagged: response.data.flagged || 0,
      fraud: response.data.fraud || 0,
      total_amount: response.data.total_amount || 0,
      avg_processing_time: response.data.avg_processing_time || '2.4 days'
    };
  } catch (error) {
    throw error.response?.data || { message: 'Failed to fetch dashboard stats' };
  }
};

// Get insurance dashboard stats
export const getInsuranceDashboardStats = async () => {
  try {
    const response = await API.get('/dashboard/stats');
    return {
      total_claims: response.data.total_claims || 0,
      fraud_probability: response.data.fraud_probability || 0,
      pending_review: response.data.pending_review || 0,
      total_amount: response.data.total_amount || 0,
      fraud_cases: response.data.fraud || 0,
      flagged_cases: response.data.flagged || 0,
      approved_cases: response.data.approved || 0,
      avg_processing_time: response.data.avg_processing_time || '2.8 days',
      accuracy_rate: '98.5%'
    };
  } catch (error) {
    throw error.response?.data || { message: 'Failed to fetch dashboard stats' };
  }
};

// Get fraud trends
export const getFraudTrends = async (period = 'month') => {
  try {
    const response = await API.get('/dashboard/fraud-trends', { params: { period } });
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Failed to fetch fraud trends' };
  }
};

// Get recent alerts
export const getRecentAlerts = async (limit = 10) => {
  try {
    const response = await API.get('/dashboard/alerts', { params: { limit } });
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Failed to fetch alerts' };
  }
};
