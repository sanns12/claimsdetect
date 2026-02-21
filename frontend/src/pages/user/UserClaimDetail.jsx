import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import Button from '../../components/Button';
import StatusBadge from '../../components/StatusBadge';
import RiskScore from '../../components/RiskScore';
import LIMEExplanation from '../../components/LIMEExplanation';
import FileUploader from '../../components/FileUploader';
import { 
  FiArrowLeft, 
  FiCalendar, 
  FiDollarSign, 
  FiUser, 
  FiActivity, 
  FiFileText,
  FiDownload,
  FiClock,
  FiCheckCircle,
  FiAlertCircle,
  FiLoader,
  FiRefreshCw
} from 'react-icons/fi';
import { CLAIM_STATUS } from '../../utils/constants';
import { getClaimById, getLimeExplanation, uploadAdditionalDocs } from '../../services/claims';
import { formatClaimFromApi } from '../../utils/apiHelpers';

export default function UserClaimDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showUploader, setShowUploader] = useState(false);
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [limeFactors, setLimeFactors] = useState([]);
  const [loadingExplanation, setLoadingExplanation] = useState(false);

  // Load claim data
  useEffect(() => {
    loadClaimData();
  }, [id]);

  const loadClaimData = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Get claim details from API
      const claimData = await getClaimById(id);
      const formattedClaim = formatClaimFromApi(claimData);
      setClaim(formattedClaim);

      // Get LIME explanation
      await loadLimeExplanation();
      
    } catch (err) {
      console.error('Failed to load claim:', err);
      setError('Failed to load claim details. Please try again.');
      
      // Fallback to localStorage
      const storedClaims = JSON.parse(localStorage.getItem('userClaims') || '[]');
      const foundClaim = storedClaims.find(c => c.id === id);
      
      if (foundClaim) {
        setClaim(foundClaim);
        // Generate mock LIME factors
        setLimeFactors(generateMockLimeFactors(foundClaim));
      } else {
        setTimeout(() => {
          navigate('/user/claims', { 
            state: { message: 'Claim not found', type: 'error' } 
          });
        }, 2000);
      }
    } finally {
      setLoading(false);
    }
  };

  const loadLimeExplanation = async () => {
    setLoadingExplanation(true);
    try {
      const explanation = await getLimeExplanation(id);
      setLimeFactors(explanation.factors);
    } catch (err) {
      console.error('Failed to load LIME explanation:', err);
      // Generate mock factors if API fails
      if (claim) {
        setLimeFactors(generateMockLimeFactors(claim));
      }
    } finally {
      setLoadingExplanation(false);
    }
  };

  const generateMockLimeFactors = (claimData) => {
    const amount = parseFloat(claimData.amount?.replace('$', '') || 5000);
    const age = parseInt(claimData.age) || 35;
    
    return [
      { 
        name: 'Claim Amount', 
        impact: amount > 10000 ? 42 : amount > 5000 ? 28 : 15,
        color: amount > 10000 ? 'high' : amount > 5000 ? 'medium' : 'low',
        description: amount > 10000 ? 'Amount significantly exceeds average' : 'Amount within normal range'
      },
      { 
        name: 'Hospital Stay Duration', 
        impact: 35,
        color: 'medium',
        description: 'Duration matches typical pattern for this condition'
      },
      { 
        name: 'Age Factor', 
        impact: age > 60 ? 30 : age < 18 ? 25 : 18,
        color: age > 60 ? 'high' : age < 18 ? 'medium' : 'low',
        description: age > 60 ? 'Higher risk demographic' : 'Standard risk profile'
      }
    ];
  };

  const handleFileDrop = (acceptedFiles) => {
    setFiles(prev => [...prev, ...acceptedFiles]);
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    
    setUploading(true);
    setError('');
    
    try {
      const result = await uploadAdditionalDocs(id, files);
      
      // Update local claim with new files
      const updatedClaim = {
        ...claim,
        documents: [...(claim.documents || []), ...result.uploadedFiles]
      };
      setClaim(updatedClaim);
      
      setFiles([]);
      setShowUploader(false);
      
    } catch (err) {
      console.error('Upload failed:', err);
      setError('Failed to upload files. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const getStayDuration = () => {
    if (claim?.admissionDate && claim?.dischargeDate) {
      const start = new Date(claim.admissionDate);
      const end = new Date(claim.dischargeDate);
      const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
      return days > 0 ? `${days} days` : 'Same day';
    }
    return null;
  };

  const buildTimeline = () => {
    const timeline = [
      { 
        status: 'Submitted', 
        date: claim?.submittedAt?.split('T')[0] || claim?.date, 
        time: claim?.submittedAt ? new Date(claim.submittedAt).toLocaleTimeString() : '10:30 AM',
        completed: true,
        description: 'Claim submitted successfully'
      }
    ];

    if (claim?.status !== CLAIM_STATUS.SUBMITTED) {
      timeline.push({
        status: 'AI Processing', 
        date: claim?.date, 
        time: '10:35 AM',
        completed: claim?.status !== CLAIM_STATUS.SUBMITTED,
        description: 'AI analysis complete'
      });
    }

    timeline.push({
      status: claim?.status === CLAIM_STATUS.APPROVED ? 'Approved' : 
               claim?.status === CLAIM_STATUS.FLAGGED ? 'Flagged' :
               claim?.status === CLAIM_STATUS.FRAUD ? 'Fraud Detected' :
               claim?.status === CLAIM_STATUS.MANUAL_REVIEW ? 'Manual Review' :
               'Processing',
      date: claim?.lastUpdated?.split('T')[0] || claim?.date,
      time: claim?.lastUpdated ? new Date(claim.lastUpdated).toLocaleTimeString() : '02:15 PM',
      completed: claim?.status === CLAIM_STATUS.APPROVED || 
                 claim?.status === CLAIM_STATUS.FLAGGED ||
                 claim?.status === CLAIM_STATUS.FRAUD,
      description: getStatusDescription(claim?.status)
    });

    return timeline;
  };

  const getStatusDescription = (status) => {
    switch(status) {
      case CLAIM_STATUS.APPROVED:
        return 'Claim has been approved for payout';
      case CLAIM_STATUS.FLAGGED:
        return 'Claim flagged for manual review based on ML analysis';
      case CLAIM_STATUS.FRAUD:
        return 'Potential fraud detected by ML model';
      case CLAIM_STATUS.MANUAL_REVIEW:
        return 'Under review by claims adjuster';
      default:
        return 'Awaiting final decision';
    }
  };

  const getTimelineIcon = (step) => {
    if (step.completed) return <FiCheckCircle className="text-success" />;
    if (step.status === 'Manual Review' || step.status === 'Flagged') 
      return <FiAlertCircle className="text-warning" />;
    if (step.status === 'Fraud Detected') 
      return <FiAlertCircle className="text-danger" />;
    return <FiLoader className="text-textSecondary animate-spin" />;
  };

  const timeline = claim ? buildTimeline() : [];

  if (loading) {
    return (
      <div className="min-h-screen bg-background text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-textSecondary">Loading claim details...</p>
        </div>
      </div>
    );
  }

  if (!claim) {
    return (
      <div className="min-h-screen bg-background text-white flex items-center justify-center">
        <div className="text-center">
          <FiAlertCircle className="text-4xl text-danger mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2">Claim Not Found</h2>
          <p className="text-textSecondary mb-4">The claim you're looking for doesn't exist</p>
          <Link to="/user/claims">
            <Button>Back to Claims</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-white">
      {/* Header */}
      <header className="bg-surface/50 backdrop-blur-sm border-b border-gray-800 sticky top-0 z-50">
        <div className="px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link 
              to="/user/claims" 
              className="p-2 hover:bg-surface rounded-lg transition-colors"
            >
              <FiArrowLeft className="text-xl" />
            </Link>
            <h1 className="text-xl font-bold">Claim {claim.id}</h1>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={loadClaimData}
              disabled={loading}
              className="p-2 hover:bg-surface rounded-lg transition-colors"
              title="Refresh"
            >
              <FiRefreshCw className={`text-textSecondary ${loading ? 'animate-spin' : ''}`} />
            </button>
            <StatusBadge status={claim.status} />
          </div>
        </div>
      </header>

      {/* Error Message */}
      {error && (
        <div className="px-6 pt-6">
          <div className="bg-danger/10 border border-danger/30 text-danger px-4 py-3 rounded-lg">
            {error}
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Claim Details & Timeline */}
          <div className="lg:col-span-2 space-y-6">
            {/* Claim Information Card */}
            <div className="bg-surface rounded-xl border border-gray-800 p-6">
              <h2 className="text-lg font-bold mb-4">Claim Information</h2>
              
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <p className="text-textSecondary text-sm mb-1">Patient Name</p>
                  <p className="font-medium flex items-center gap-2">
                    <FiUser className="text-primary" />
                    {claim.patientName || 'John Doe'}
                  </p>
                </div>
                <div>
                  <p className="text-textSecondary text-sm mb-1">Age</p>
                  <p className="font-medium">{claim.age || '35'} years</p>
                </div>
                <div>
                  <p className="text-textSecondary text-sm mb-1">Admission Date</p>
                  <p className="font-medium flex items-center gap-2">
                    <FiCalendar className="text-primary" />
                    {claim.admissionDate || claim.date}
                  </p>
                </div>
                <div>
                  <p className="text-textSecondary text-sm mb-1">Discharge Date</p>
                  <p className="font-medium flex items-center gap-2">
                    <FiCalendar className="text-primary" />
                    {claim.dischargeDate || claim.date}
                  </p>
                </div>
                <div>
                  <p className="text-textSecondary text-sm mb-1">Disease/Condition</p>
                  <p className="font-medium flex items-center gap-2">
                    <FiActivity className="text-primary" />
                    {claim.disease || 'General Checkup'}
                  </p>
                </div>
                <div>
                  <p className="text-textSecondary text-sm mb-1">Claim Amount</p>
                  <p className="font-medium text-xl flex items-center gap-2">
                    <FiDollarSign className="text-primary" />
                    {claim.amount}
                  </p>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t border-gray-800">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="text-textSecondary text-sm mb-1">Hospital</p>
                    <p className="font-medium">{claim.hospital || 'City General Hospital'}</p>
                  </div>
                  {getStayDuration() && (
                    <div className="text-right">
                      <p className="text-textSecondary text-sm mb-1">Stay Duration</p>
                      <p className="font-medium text-primary">{getStayDuration()}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Status Timeline */}
            <div className="bg-surface rounded-xl border border-gray-800 p-6">
              <h2 className="text-lg font-bold mb-4">Claim Timeline</h2>
              
              <div className="space-y-4">
                {timeline.map((step, index) => (
                  <div key={index} className="flex gap-4">
                    <div className="relative">
                      <div className="w-8 h-8 rounded-full bg-background flex items-center justify-center">
                        {getTimelineIcon(step)}
                      </div>
                      {index < timeline.length - 1 && (
                        <div className="absolute top-8 left-4 w-0.5 h-12 bg-gray-800"></div>
                      )}
                    </div>
                    <div className="flex-1 pb-4">
                      <div className="flex items-center justify-between">
                        <h3 className="font-medium">{step.status}</h3>
                        {step.date && (
                          <span className="text-sm text-textSecondary flex items-center gap-1">
                            <FiClock />
                            {step.date} {step.time}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-textSecondary mt-1">{step.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column - Risk Score & Documents */}
          <div className="space-y-6">
            {/* Risk Score Card */}
            <div className="bg-surface rounded-xl border border-gray-800 p-6">
              <h2 className="text-lg font-bold mb-4">ML Risk Analysis</h2>
              
              <div className="flex justify-center mb-6">
                <RiskScore score={claim.risk || 45} />
              </div>

              {/* LIME Explanation */}
              <LIMEExplanation 
                factors={limeFactors}
                loading={loadingExplanation}
              />
            </div>

            {/* Documents Card */}
            <div className="bg-surface rounded-xl border border-gray-800 p-6">
              <h2 className="text-lg font-bold mb-4">Documents</h2>
              
              {/* Existing Documents */}
              {claim.documents && claim.documents.length > 0 ? (
                <div className="space-y-3 mb-4">
                  {claim.documents.map((doc, index) => (
                    <div key={index} className="flex items-center justify-between bg-background p-3 rounded-lg">
                      <div className="flex items-center gap-3">
                        <FiFileText className="text-primary" />
                        <span className="text-sm">{typeof doc === 'string' ? doc : doc.name}</span>
                      </div>
                      <button 
                        className="text-textSecondary hover:text-primary transition-colors"
                        onClick={() => window.open(`http://localhost:8000/api/claims/${id}/documents/${index}`, '_blank')}
                      >
                        <FiDownload />
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-textSecondary text-sm mb-4">No documents uploaded yet</p>
              )}

              {/* Upload New Documents */}
              {!showUploader ? (
                <Button 
                  variant="secondary" 
                  className="w-full"
                  onClick={() => setShowUploader(true)}
                >
                  Upload Additional Documents
                </Button>
              ) : (
                <div className="space-y-4">
                  <FileUploader onDrop={handleFileDrop} />
                  
                  {files.length > 0 && (
                    <div className="space-y-2">
                      {files.map((file, index) => (
                        <div key={index} className="flex items-center justify-between bg-background p-2 rounded text-sm">
                          <span>{file.name}</span>
                          <button 
                            onClick={() => removeFile(index)}
                            className="text-danger text-xs"
                          >
                            Remove
                          </button>
                        </div>
                      ))}
                      <Button 
                        onClick={handleUpload}
                        disabled={uploading}
                        className="w-full mt-2"
                      >
                        {uploading ? 'Uploading...' : `Upload ${files.length} File${files.length > 1 ? 's' : ''}`}
                      </Button>
                    </div>
                  )}
                  
                  <button 
                    onClick={() => setShowUploader(false)}
                    className="text-sm text-textSecondary hover:text-primary w-full text-center"
                  >
                    Cancel
                  </button>
                </div>
              )}
            </div>

            {/* Status-specific messages */}
            {claim.status === CLAIM_STATUS.FLAGGED && (
              <div className="bg-warning/10 border border-warning/30 rounded-xl p-4">
                <p className="text-warning text-sm">
                  This claim has been flagged for manual review. You may need to provide additional information.
                </p>
              </div>
            )}

            {claim.status === CLAIM_STATUS.FRAUD && (
              <div className="bg-danger/10 border border-danger/30 rounded-xl p-4">
                <p className="text-danger text-sm">
                  Potential fraud detected. Please contact support immediately.
                </p>
              </div>
            )}

            {claim.status === CLAIM_STATUS.APPROVED && (
              <div className="bg-success/10 border border-success/30 rounded-xl p-4">
                <p className="text-success text-sm">
                  Claim approved! Payment will be processed within 3-5 business days.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
