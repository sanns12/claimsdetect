// Handle API errors gracefully
export const handleApiError = (error, fallbackMessage = 'An error occurred') => {
  if (error.response) {
    // Server responded with error
    return error.response.data.message || fallbackMessage;
  } else if (error.request) {
    // Request made but no response
    return 'No response from server. Please check your connection.';
  } else {
    // Something else happened
    return error.message || fallbackMessage;
  }
};

// Format claim data for API submission
export const formatClaimForApi = (formData) => {
  return {
    patient_id: formData.patientId,
    patient_name: formData.patientName,
    age: parseInt(formData.age),
    gender: formData.gender,
    admission_date: formData.admissionDate,
    discharge_date: formData.dischargeDate,
    diagnosis: formData.diagnosis,
    procedure: formData.procedure,
    claim_amount: parseFloat(formData.amount),
    department: formData.department,
    doctor_name: formData.doctorName,
    insurance_provider: formData.insuranceProvider,
    policy_number: formData.policyNumber,
    hospital_id: formData.hospitalId || 'HOSP-001',
    submitted_at: new Date().toISOString()
  };
};

// Format API response for frontend display
export const formatClaimFromApi = (apiClaim) => {
  const rawRisk = apiClaim.risk ?? apiClaim.risk_score ?? apiClaim.fraudScore ?? apiClaim.fraud_score ?? 0;
  const normalizeRisk = (value) => {
    if (typeof value === 'number') {
      return value <= 1 ? Math.round(value * 100) : Math.round(value);
    }
    return 0;
  };

  const normalizeStatus = (value) => {
    if (!value) return 'Submitted';
    const status = String(value).trim().toLowerCase();
    switch (status) {
      case 'submitted':
        return 'Submitted';
      case 'approved':
        return 'Approved';
      case 'flagged':
        return 'Flagged';
      case 'fraud':
      case 'fraud detected':
        return 'Fraud';
      case 'manual review':
        return 'Manual Review';
      default:
        return String(value);
    }
  };

  const normalizedRisk = normalizeRisk(rawRisk);

  return {
    id: apiClaim.id || apiClaim.claim_id,
    patientId: apiClaim.patient_id,
    patientName: apiClaim.patient_name || 'N/A',
    age: apiClaim.age,
    gender: apiClaim.gender,
    date: apiClaim.date || apiClaim.created_at || (apiClaim.submitted_at || '').split('T')[0],
    amount: typeof apiClaim.claim_amount === 'number' 
      ? `$${apiClaim.claim_amount.toLocaleString()}` 
      : apiClaim.amount || '$0',
    status: normalizeStatus(apiClaim.status),
    risk: normalizedRisk,
    risk_score: normalizedRisk,
    department: apiClaim.department,
    diagnosis: apiClaim.diagnosis || apiClaim.disease,
    disease: apiClaim.disease || apiClaim.diagnosis,
    doctor: apiClaim.doctor_name,
    insuranceProvider: apiClaim.insurance_provider,
    policyNumber: apiClaim.policy_number,
    admissionDate: apiClaim.admission_date,
    dischargeDate: apiClaim.discharge_date,
    hospital: apiClaim.hospital_name,
    documents: apiClaim.documents || [],
    submittedAt: apiClaim.submitted_at || apiClaim.created_at,
    lastUpdated: apiClaim.updated_at,
    mismatchWarnings: apiClaim.mismatch_warnings || []
  };
};
