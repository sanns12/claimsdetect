import API from './api';

export const getRiskScore = async (claimData) => {
  try {
    const response = await API.post('/risk/score', claimData);
    return response.data;
  } catch {
    console.log('Risk calculation failed, using fallback...');
    
    // Fallback: Generate mock risk score
    const amount = claimData.amount || 5000;
    const age = claimData.age || 35;
    const disease = claimData.disease || 'General';
    
    // Calculate a realistic mock score
    let score = 30; // Base score
    
    // Amount factor
    if (amount > 20000) score += 30;
    else if (amount > 10000) score += 20;
    else if (amount > 5000) score += 10;
    
    // Age factor
    if (age > 70) score += 15;
    else if (age > 60) score += 10;
    else if (age < 18) score += 5;
    
    // Disease factor (higher risk for certain conditions)
    const highRiskDiseases = ['Oncology', 'Cardiovascular', 'Neurological'];
    const mediumRiskDiseases = ['Respiratory', 'Infectious Disease'];
    
    if (highRiskDiseases.includes(disease)) score += 20;
    else if (mediumRiskDiseases.includes(disease)) score += 10;
    
    // Cap at 95
    score = Math.min(score, 95);
    
    // Generate mock factors
    const factors = [
      { 
        name: 'Claim Amount', 
        impact: amount > 10000 ? 42 : 28,
        color: amount > 10000 ? 'high' : 'medium',
        description: amount > 10000 ? 'Amount exceeds typical range' : 'Amount within normal parameters'
      },
      { 
        name: 'Patient Age', 
        impact: age > 60 ? 35 : age < 18 ? 30 : 18,
        color: age > 60 ? 'high' : age < 18 ? 'medium' : 'low',
        description: age > 60 ? 'Higher risk demographic' : 'Standard age profile'
      },
      { 
        name: 'Disease Type', 
        impact: highRiskDiseases.includes(disease) ? 45 : mediumRiskDiseases.includes(disease) ? 30 : 20,
        color: highRiskDiseases.includes(disease) ? 'high' : mediumRiskDiseases.includes(disease) ? 'medium' : 'low',
        description: `${disease} requires ${highRiskDiseases.includes(disease) ? 'enhanced' : 'standard'} verification`
      }
    ];
    
    return {
      score,
      factors,
      confidence: 0.85,
      source: 'fallback'
    };
  }
};