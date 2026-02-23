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
// Submit a new claim with documents (OCR ENABLED)
export const submitClaim = async (claimData, file) => {
  if (!file) {
    throw { message: "Supporting document is required." };
  }

  const formData = new FormData();

  formData.append("patient_name", claimData.patient_name);
  formData.append("age", claimData.age);
  formData.append("disease", claimData.disease);
  formData.append("admission_date", claimData.admission_date);
  formData.append("discharge_date", claimData.discharge_date);
  formData.append("claim_amount", claimData.claim_amount);
  formData.append("hospital_name", claimData.hospital_name);
  formData.append("supporting_file", file);

  const response = await API.post("/claims/submit", formData);
  return response.data;
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
