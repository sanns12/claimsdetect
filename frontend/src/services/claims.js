import API from './api';

// Get all claims with filters
export const getClaims = async (filters = {}) => {
  try {
    const response = await API.get('/claims', { params: filters });
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Failed to fetch claims' };
  }
};

// Get single claim by ID
export const getClaimById = async (claimId) => {
  try {
    const response = await API.get(`/claims/${claimId}`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Failed to fetch claim details' };
  }
};

// Submit a new claim with documents
export const submitClaim = async (claimData) => {
  try {
    // Format data to match backend ClaimSubmission schema
    const formattedData = {
      age: parseInt(claimData.age) || 0,
      disease: claimData.disease || '',
      admission_date: claimData.admissionDate || claimData.admission_date || '',
      discharge_date: claimData.dischargeDate || claimData.discharge_date || '',
      claim_amount: parseFloat(claimData.amount || claimData.claim_amount) || 0,
      patient_name: claimData.fullName || claimData.patient_name || '',
      hospital_name: claimData.hospital || claimData.hospital_name || 'City General Hospital',
    };

    console.log('Submitting claim with data:', formattedData);

    const response = await API.post('/claims/submit', formattedData);
    return response.data;
  } catch (error) {
    console.error('Submit claim error:', error.response?.data || error);
    throw error.response?.data || { message: 'Claim submission failed' };
  }
};
// Delete claim
export const deleteClaim = async (claimId) => {
  try {
    const response = await API.delete(`/claims/${claimId}`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Failed to delete claim' };
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

// Get LIME explanation
export const getLimeExplanation = async (claimId) => {
  try {
    const response = await API.get(`/claims/${claimId}/explain`);
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Failed to get explanation' };
  }
};

// Role-specific aliases
export const getUserClaims = async (filters = {}) => {
  return getClaims({ ...filters, role: 'user' });
};

export const getHospitalClaims = async (filters = {}) => {
  return getClaims({ ...filters, role: 'hospital' });
};

export const getAllClaims = async (filters = {}) => {
  return getClaims(filters);
};
