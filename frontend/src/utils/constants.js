export const CLAIM_STATUS = {
  SUBMITTED: 'Submitted',
  AI_PROCESSING: 'AI Processing',
  MANUAL_REVIEW: 'Manual Review',
  APPROVED: 'Approved',
  FLAGGED: 'Flagged',
  FRAUD: 'Fraud',
};

export const STATUS_COLORS = {
  [CLAIM_STATUS.SUBMITTED]: '#8B8F95',
  [CLAIM_STATUS.AI_PROCESSING]: '#3B82F6',
  [CLAIM_STATUS.MANUAL_REVIEW]: '#F59E0B',
  [CLAIM_STATUS.APPROVED]: '#10B981',
  [CLAIM_STATUS.FLAGGED]: '#F59E0B',
  [CLAIM_STATUS.FRAUD]: '#EF4444',
};

export const USER_ROLES = {
  USER: 'User',
  HOSPITAL: 'Hospital',
  INSURANCE: 'Insurance',
};
