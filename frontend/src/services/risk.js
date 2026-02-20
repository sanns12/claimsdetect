import API from './api';

// Get risk score for a claim
export const getRiskScore = async (claimData) => {
  try {
    const response = await API.post('/risk/score', claimData);
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Risk scoring failed' };
  }
};

// Get company trust score
export const getCompanyTrustScore = async (companyId) => {
  try {
    const response = await API.get(`/trust/company/${companyId}`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Failed to get trust score' };
  }
};

// Get all companies with trust scores
export const getAllCompaniesTrust = async () => {
  try {
    const response = await API.get('/trust/companies');
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Failed to fetch companies' };
  }
};
