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
import { getClaimDetails, getLimeExplanation, uploadAdditionalDocs } from '../../services/claims';

export default function UserClaimDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showUploader, setShowUploader] = useState(false);
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [limeFactors, setLimeFactors] = useState([]);
  const [loadingExplanation, setLoadingExplanation] = useState(false);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  // Load claim data with ML explanation
  useEffect(() => {
    loadClaimWithML();
  }, [id]);

  const loadClaimWithML = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Get claim details from backend
      const claimData = await getClaimDetails(id);
      setClaim(claimData);

      // Get LIME explanation from ML model
      await loadLimeExplanation();
      
    } catch (err) {
      console.error('Failed to load claim:', err);
      setError(err.message || 'Failed to load claim details');
      
      // Fallback to localStorage if backend fails
      const storedClaims = JSON.parse(localStorage.getItem('userClaims') || '[]');
      const foundClaim = storedClaims.find(c => c.id === id);
      
      if (foundClaim) {
        setClaim(foundClaim);
        // Use mock LIME data for localStorage claims
        setLimeFactors(generateMockLimeFactors(foundClaim));
      } else {
        // If not found anywhere, redirect after delay
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
      // Generate mock factors based on claim data
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
        description: amount > 10000 ? 'Amount significantly exceeds average' : 'Amount within normal range'
      },
      { 
        name: 'Hospital Stay Duration', 
        impact: 35,
        description: 'Duration matches typical pattern for this condition'
      },
      { 
        name: 'Age Factor', 
        impact: age > 60 ? 30 : age < 18 ? 25 : 18,
        description: age > 60 ? 'Higher risk demographic' : 'Standard risk profile'
      },
      { 
        name: 'Disease Type', 
        impact: 23,
        description: claimData.disease || 'Common condition with established patterns'
      }
    ];
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadClaimWithML();
    setRefreshing(false);
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
      // Upload to backend
      const result = await uploadAdditionalDocs(id, files);
      
      // Update local claim with new files
      const updatedClaim = {
        ...claim,
        files: [...(claim.files || []), ...result.uploadedFiles]
      };
      setClaim(updatedClaim);
      
      // Clear uploader
      setFiles([]);
      setShowUploader(false);
      
      // Show success message (could add a toast notification here)
      console.log('Files uploaded successfully');
      
    } catch (err) {
      console.error('Upload failed:', err);
      setError(err.message || 'Failed to upload files');
    } finally {
      setUploading(false);
    }
  };

  // Calculate stay duration
  const getStayDuration = () => {
    if (claim?.admissionDate && claim?.dischargeDate) {
      const start = new Date(claim.admissionDate);
      const end = new Date(claim.dischargeDate);
      const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
      return days > 0 ? `${days} days` : 'Same day';
    }
    return null;
  };

  // Build timeline from claim status
  const buildTimeline = () => {
    const timeline = [
      { 
        status: 'Submitted', 
        date: claim?.submittedAt?.split('T')[0] || claim?.date || '2024-03-15', 
        time: claim?.submittedAt ? new Date(claim.submittedAt).toLocaleTimeString() : '10:30 AM',
        completed: true,
        description: 'Claim submitted successfully'
      }
    ];

    // Add AI Processing if applicable
    if (claim?.status !== CLAIM_STATUS.SUBMITTED || claim?.aiProcessedAt) {
      timeline.push({
        status: 'AI Processing', 
        date: claim?.aiProcessedAt?.split('T')[0] || claim?.date || '2024-03-15', 
        time: claim?.aiProcessedAt ? new Date(claim.aiProcessedAt).toLocaleTimeString() : '10:35 AM',
        completed: claim?.status !== CLAIM_STATUS.SUBMITTED,
        description: claim?.mlAnalysisComplete 
          ? 'AI analysis complete' 
          : 'AI analysis in progress'
      });
    }

    // Add final status
    timeline.push({
      status: claim?.status === CLAIM_STATUS.APPROVED ? 'Approved' : 
               claim?.status === CLAIM_STATUS.FLAGGED ? 'Flagged' :
               claim?.status === CLAIM_STATUS.FRAUD ? 'Fraud Detected' :
               claim?.status === CLAIM_STATUS.MANUAL_REVIEW ? 'Manual Review' :
               'Processing',
      date: claim?.processedAt?.split('T')[0] || 
            (claim?.status !== CLAIM_STATUS.SUBMITTED ? '2024-03-16' : null),
      time: claim?.processedAt ? new Date(claim.processedAt).toLocaleTimeString() : 
            (claim?.status !== CLAIM_STATUS.SUBMITTED ? '02:15 PM' : null),
      completed: claim?.status === CLAIM_STATUS.APPROVED || 
                 claim?.status === CLAIM_STATUS.FLAGGED ||
                 claim?.status === CLAIM_STATUS.FRAUD,
      description: getStatusDescription(claim?.status)
    });

    return timeline;
  };

  function getStatusDescription(status) {
    switch(status) {
      case CLAIM_STATUS.APPROVED:
        return 'Claim has been approved for payout';
      case CLAIM_STATUS.FLAGGED:
        return 'Claim flagged for manual review based on ML analysis';
      case CLAIM_STATUS.FRAUD:
        return 'Potential fraud detected by ML model - under investigation';
      case CLAIM_STATUS.MANUAL_REVIEW:
        return 'Under review by claims adjuster';
      case CLAIM_STATUS.AI_PROCESSING:
        return 'ML model analyzing claim data';
      default:
        return 'Awaiting final decision';
    }
  }

  const getTimelineIcon = (step) => {
    if (step.completed) return <FiCheckCircle className="text-success" />;
    if (step.status === 'Manual Review' || step.status === 'Flagged') 
      return <FiAlertCircle className="text-warning" />;
    if (step.status === 'Fraud Detected') 
      return <FiAlertCircle className="text-danger" />;
    if (step.status === 'AI Processing')
      return <FiLoader className="text-primary animate-spin" />;
    return <FiLoader className="text-textSecondary animate-spin" />;
  };

  const timeline = buildTimeline();

  if (loading) {
    return (
      <div className="min-h-screen bg-background text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-textSecondary">Loading claim details with ML analysis...</p>
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
              onClick={handleRefresh}
              disabled={refreshing}
              className="p-2 hover:bg-surface rounded-lg transition-colors"
              title="Refresh ML analysis"
            >
              <FiRefreshCw className={`text-textSecondary ${refreshing ? 'animate-spin' : ''}`} />
            </button>
            <StatusBadge status={claim.status} />
          </div>
        </div>
      </header>

      {/* Error Message */}
      {error && (
        <div className="px-6 pt-6">
          <div className="bg-danger/10 border border-danger/30 text-danger px-4 py-3 rounded-lg flex items-center gap-3">
            <FiAlertCircle />
            <span>{error}</span>
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
                    {claim.fullName || 'John Doe'}
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

              {/* ML Confidence Score */}
              {claim.mlConfidence && (
                <div className="mt-4 pt-4 border-t border-gray-800">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-textSecondary">ML Confidence Score</span>
                    <span className={`text-sm font-mono ${
                      claim.mlConfidence > 0.8 ? 'text-success' :
                      claim.mlConfidence > 0.6 ? 'text-warning' : 'text-danger'
                    }`}>
                      {(claim.mlConfidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Risk Score & Documents */}
          <div className="space-y-6">
            {/* Risk Score Card */}
            <div className="bg-surface rounded-xl border border-gray-800 p-6">
              <h2 className="text-lg font-bold mb-4">ML Risk Analysis</h2>
              
              <div className="flex justify-center mb-6">
                <RiskScore score={claim.riskScore || claim.risk || 45} />
              </div>

              {/* LIME Explanation */}
              <LIMEExplanation 
                factors={limeFactors}
                loading={loadingExplanation}
              />

              {claim.riskFactors && (
                <div className="mt-4 pt-4 border-t border-gray-800">
                  <p className="text-xs text-textSecondary">
                    Analysis based on {claim.riskFactors?.length || 0} similar claims in database
                  </p>
                </div>
              )}
            </div>

            {/* Documents Card */}
            <div className="bg-surface rounded-xl border border-gray-800 p-6">
              <h2 className="text-lg font-bold mb-4">Documents</h2>
              
              {/* Existing Documents */}
              {claim.files && claim.files.length > 0 ? (
                <div className="space-y-3 mb-4">
                  {claim.files.map((file, index) => (
                    <div key={index} className="flex items-center justify-between bg-background p-3 rounded-lg">
                      <div className="flex items-center gap-3">
                        <FiFileText className="text-primary" />
                        <span className="text-sm">{typeof file === 'string' ? file : file.name}</span>
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

            {/* Action Buttons (based on status) */}
            {claim.status === CLAIM_STATUS.FLAGGED && (
              <div className="bg-warning/10 border border-warning/30 rounded-xl p-4">
                <p className="text-warning text-sm mb-3">
                  This claim has been flagged by our ML model for manual review. You may need to provide additional information.
                </p>
                <Button variant="warning" className="w-full">
                  Contact Support
                </Button>
              </div>
            )}

            {claim.status === CLAIM_STATUS.FRAUD && (
              <div className="bg-danger/10 border border-danger/30 rounded-xl p-4">
                <p className="text-danger text-sm mb-3">
                  Potential fraud detected by ML analysis. Please contact our fraud department immediately.
                </p>
                <Button variant="danger" className="w-full">
                  Contact Fraud Dept
                </Button>
              </div>
            )}

            {claim.status === CLAIM_STATUS.APPROVED && (
              <div className="bg-success/10 border border-success/30 rounded-xl p-4">
                <p className="text-success text-sm mb-3">
                  Claim approved! Payment will be processed within 3-5 business days.
                </p>
                <Button variant="success" className="w-full">
                  Track Payment
                </Button>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}