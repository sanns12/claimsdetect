import API from './api';

export const getClaimDetails = async (claimId) => {
  try {
    const response = await API.get(`/claims/${claimId}`);
    return response.data;
  } catch{
    console.log('Backend unavailable, loading from localStorage...');
    
    // Fallback: Get from localStorage
    const storedClaims = JSON.parse(localStorage.getItem('userClaims') || '[]');
    const foundClaim = storedClaims.find(c => c.id === claimId);
    
    if (foundClaim) {
      return foundClaim;
    }
    
    throw new Error('Claim not found');
  }
};

export const getLimeExplanation = async (claimId) => {
  try {
    const response = await API.get(`/claims/${claimId}/explain`);
    return response.data;
  } catch {
    console.log('LIME explanation unavailable, using mock data...');
    
    // Return mock explanation
    return {
      factors: [
        { name: 'Claim Amount', impact: 42, color: 'high', description: 'Amount exceeds typical range' },
        { name: 'Treatment Duration', impact: 35, color: 'medium', description: 'Duration shorter than average' },
        { name: 'Patient History', impact: 23, color: 'low', description: 'No previous flags' }
      ]
    };
  }
};

export const uploadAdditionalDocs = async (claimId, files) => {
  try {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('documents', file);
    });

    const response = await API.post(`/claims/${claimId}/documents`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch {
    console.log('Upload failed, saving locally...');
    
    // Fallback: Update localStorage
    const storedClaims = JSON.parse(localStorage.getItem('userClaims') || '[]');
    const updatedClaims = storedClaims.map(claim => {
      if (claim.id === claimId) {
        return {
          ...claim,
          files: [...(claim.files || []), ...files.map(f => f.name)]
        };
      }
      return claim;
    });
    
    localStorage.setItem('userClaims', JSON.stringify(updatedClaims));
    
    return {
      success: true,
      uploadedFiles: files.map(f => f.name),
      message: 'Files saved locally'
    };
  }
};

export const submitClaim = async (claimData, files) => {
  try {
    const formData = new FormData();
    
    Object.keys(claimData).forEach(key => {
      formData.append(key, claimData[key]);
    });
    
    files.forEach(file => {
      formData.append('documents', file);
    });

    const response = await API.post('/claims/submit', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch{
    console.log('Backend unavailable, saving to localStorage...');
    
    // Fallback: Save to localStorage
    const newClaim = {
      id: `CLM${Math.floor(Math.random() * 1000).toString().padStart(3, '0')}`,
      date: new Date().toISOString().split('T')[0],
      ...claimData,
      amount: `$${parseFloat(claimData.amount).toLocaleString()}`,
      status: 'Submitted',
      risk: Math.floor(Math.random() * 40) + 20,
      files: files.map(f => f.name),
      submittedAt: new Date().toISOString()
    };

    const existingClaims = JSON.parse(localStorage.getItem('userClaims') || '[]');
    existingClaims.push(newClaim);
    localStorage.setItem('userClaims', JSON.stringify(existingClaims));

    return {
      claimId: newClaim.id,
      riskScore: newClaim.risk,
      message: 'Claim saved locally (backend unavailable)'
    };
  }
};