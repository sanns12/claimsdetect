import API from './api';

// Get all companies
export const getAllCompanies = async (filters = {}) => {
  try {
    const response = await API.get('/companies', { params: filters });
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Failed to fetch companies' };
  }
};

// Get company by ID
export const getCompanyById = async (companyId) => {
  try {
    const response = await API.get(`/companies/${companyId}`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Failed to fetch company details' };
  }
};

// Get company trust score
export const getCompanyTrustScore = async (companyId) => {
  try {
    const response = await API.get(`/companies/${companyId}/trust-score`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Failed to get trust score' };
  }
};

// Get high-risk companies
export const getHighRiskCompanies = async (limit = 10) => {
  try {
    const response = await API.get('/companies/high-risk/list', { params: { limit } });
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Failed to fetch high-risk companies' };
  }
};

// Update company trust level (insurance only)
export const updateCompanyTrustLevel = async (companyId, trustLevel, reason) => {
  try {
    const response = await API.patch(`/companies/${companyId}/trust-level`, {
      trust_level: trustLevel,
      reason
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Failed to update trust level' };
  }
};