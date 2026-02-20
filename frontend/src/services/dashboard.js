import API from './api';

export const getUserDashboardStats = async () => {
  try {
    const response = await API.get('/dashboard/user');
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Failed to fetch dashboard stats' };
  }
};

export const getHospitalDashboardStats = async () => {
  try {
    const response = await API.get('/dashboard/hospital');
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Failed to fetch dashboard stats' };
  }
};

export const getInsuranceDashboardStats = async () => {
  try {
    const response = await API.get('/dashboard/insurance');
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Failed to fetch dashboard stats' };
  }
};
