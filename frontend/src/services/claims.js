import API from './api';

// Submit a new claim with documents
export const submitClaim = async (claimData, files) => {
  const formData = new FormData();
  
  // Append claim data
  Object.keys(claimData).forEach(key => {
    formData.append(key, claimData[key]);
  });
  
  // Append files
  files.forEach(file => {
    formData.append('documents', file);
  });

  try {
    const response = await API.post('/claims/submit', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Claim submission failed' };
  }
};

// Get all claims for a user
export const getUserClaims = async (filters = {}) => {
  try {
    const response = await API.get('/claims/user', { params: filters });
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Failed to fetch claims' };
  }
};

// Get single claim with ML analysis
export const getClaimDetails = async (claimId) => {
  try {
    const response = await API.get(`/claims/${claimId}`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Failed to fetch claim details' };
  }
};

// Get LIME explanation for a claim
export const getLimeExplanation = async (claimId) => {
  try {
    const response = await API.get(`/claims/${claimId}/explain`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Failed to get explanation' };
  }
};

// Upload additional documents
export const uploadAdditionalDocs = async (claimId, files) => {
  const formData = new FormData();
  files.forEach(file => {
    formData.append('documents', file);
  });

  try {
    const response = await API.post(`/claims/${claimId}/documents`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Upload failed' };
  }
};
