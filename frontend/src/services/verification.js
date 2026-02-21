import API from './api';

// Verify a single document
export const verifyDocument = async (file) => {
  const formData = new FormData();
  formData.append('document', file);

  try {
    const response = await API.post('/verification/verify-document', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Document verification failed' };
  }
};

// Batch verify documents
export const batchVerifyDocuments = async (files) => {
  const formData = new FormData();
  files.forEach(file => {
    formData.append('documents', file);
  });

  try {
    const response = await API.post('/verification/batch-verify', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Batch verification failed' };
  }
};

// Check document authenticity
export const checkDocumentAuthenticity = async (file) => {
  const formData = new FormData();
  formData.append('document', file);

  try {
    const response = await API.post('/verification/check-authenticity', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || { message: 'Authenticity check failed' };
  }
};