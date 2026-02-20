import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
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
  FiRefreshCw,
  FiEdit,
  FiMessageSquare,
  FiEye,
  FiPrinter
} from 'react-icons/fi';
import { CLAIM_STATUS } from '../../utils/constants';

export default function HospitalClaimDetail() {
  const { id } = useParams();
  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showUploader, setShowUploader] = useState(false);
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [notes, setNotes] = useState('');
  const [showNotes, setShowNotes] = useState(false);
  const [limeFactors, setLimeFactors] = useState([]);

  const loadClaim = useCallback(() => {
    // Mock data - replace with API call
    setTimeout(() => {
      const mockClaim = {
        id: id,
        patientId: 'P100234',
        patientName: 'Sarah Johnson',
        age: 45,
        gender: 'Female',
        date: '2024-03-20',
        amount: 5200,
        status: CLAIM_STATUS.FLAGGED,
        risk: 76,
        department: 'Cardiology',
        diagnosis: 'Cardiovascular Disease',
        doctor: 'Dr. Williams',
        insuranceProvider: 'Blue Cross',
        policyNumber: 'BC-789012',
        admissionDate: '2024-03-15',
        dischargeDate: '2024-03-18',
        documents: [
          { name: 'admission_form.pdf', size: '245 KB' },
          { name: 'lab_results.pdf', size: '1.2 MB' },
          { name: 'discharge_summary.pdf', size: '892 KB' }
        ],
        medicalNotes: [
          { 
            author: 'Dr. Williams', 
            date: '2024-03-19', 
            time: '14:30',
            content: 'Patient showing good response to treatment. No complications.'
          },
          { 
            author: 'Nurse Johnson', 
            date: '2024-03-18', 
            time: '09:15',
            content: 'Vitals stable. Pain managed with medication.'
          }
        ],
        submittedBy: 'Dr. Williams',
        submittedAt: '2024-03-20T10:30:00',
        lastUpdated: '2024-03-20T14:25:00',
        priority: 'high'
      };
      
      setClaim(mockClaim);
      
      // Mock LIME factors
      setLimeFactors([
        { 
          name: 'Claim Amount', 
          impact: 42, 
          color: 'high',
          description: 'Amount exceeds typical range for this condition'
        },
        { 
          name: 'Hospital Stay Duration', 
          impact: 35, 
          color: 'medium',
          description: 'Stay duration is shorter than average'
        },
        { 
          name: 'Patient Age', 
          impact: 23, 
          color: 'low',
          description: 'Age within normal risk parameters'
        }
      ]);
      
      setLoading(false);
    }, 1000);
  }, [id]);

  // Load claim data
  useEffect(() => {
    loadClaim();
  }, [loadClaim]);

  const handleFileDrop = (acceptedFiles) => {
    setFiles(prev => [...prev, ...acceptedFiles]);
  };

  const handleUpload = () => {
    setUploading(true);
    setTimeout(() => {
      setUploading(false);
      setShowUploader(false);
      setFiles([]);
      // Show success message
    }, 1500);
  };

  const handleAddNote = () => {
    if (notes.trim()) {
      // Add note logic here
      setNotes('');
      setShowNotes(false);
    }
  };

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
          <Link to="/hospital/claims">
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
              to="/hospital/claims" 
              className="p-2 hover:bg-surface rounded-lg transition-colors"
            >
              <FiArrowLeft className="text-xl" />
            </Link>
            <h1 className="text-xl font-bold">Claim {claim.id}</h1>
            <StatusBadge status={claim.status} />
          </div>
          <div className="flex items-center gap-3">
            <Button 
              variant="secondary" 
              size="sm"
              onClick={() => window.print()}
            >
              <FiPrinter className="mr-2" />
              Print
            </Button>
            <Button 
              variant="secondary" 
              size="sm"
              onClick={loadClaim}
            >
              <FiRefreshCw className="mr-2" />
              Refresh
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Patient & Claim Details */}
          <div className="lg:col-span-2 space-y-6">
            {/* Patient Information Card */}
            <div className="bg-surface rounded-xl border border-gray-800 p-6">
              <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                <FiUser className="text-primary" />
                Patient Information
              </h2>
              
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-textSecondary text-xs">Patient ID</p>
                  <p className="font-medium">{claim.patientId}</p>
                </div>
                <div>
                  <p className="text-textSecondary text-xs">Full Name</p>
                  <p className="font-medium">{claim.patientName}</p>
                </div>
                <div>
                  <p className="text-textSecondary text-xs">Age/Gender</p>
                  <p className="font-medium">{claim.age}y / {claim.gender}</p>
                </div>
              </div>
            </div>

            {/* Claim Details Card */}
            <div className="bg-surface rounded-xl border border-gray-800 p-6">
              <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                <FiActivity className="text-primary" />
                Claim Details
              </h2>
              
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-textSecondary text-xs">Admission Date</p>
                  <p className="font-medium flex items-center gap-1">
                    <FiCalendar className="text-primary text-sm" />
                    {claim.admissionDate}
                  </p>
                </div>
                <div>
                  <p className="text-textSecondary text-xs">Discharge Date</p>
                  <p className="font-medium flex items-center gap-1">
                    <FiCalendar className="text-primary text-sm" />
                    {claim.dischargeDate}
                  </p>
                </div>
                <div>
                  <p className="text-textSecondary text-xs">Diagnosis</p>
                  <p className="font-medium">{claim.diagnosis}</p>
                </div>
                <div>
                  <p className="text-textSecondary text-xs">Department</p>
                  <p className="font-medium">{claim.department}</p>
                </div>
                <div>
                  <p className="text-textSecondary text-xs">Attending Doctor</p>
                  <p className="font-medium">{claim.doctor}</p>
                </div>
                <div>
                  <p className="text-textSecondary text-xs">Claim Amount</p>
                  <p className="font-medium text-xl text-success">
                    ${claim.amount.toLocaleString()}
                  </p>
                </div>
              </div>
            </div>

            {/* Insurance Information */}
            <div className="bg-surface rounded-xl border border-gray-800 p-6">
              <h2 className="text-lg font-bold mb-4">Insurance Information</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-textSecondary text-xs">Provider</p>
                  <p className="font-medium">{claim.insuranceProvider}</p>
                </div>
                <div>
                  <p className="text-textSecondary text-xs">Policy Number</p>
                  <p className="font-medium">{claim.policyNumber}</p>
                </div>
              </div>
            </div>

            {/* Medical Notes */}
            <div className="bg-surface rounded-xl border border-gray-800 p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-bold flex items-center gap-2">
                  <FiMessageSquare className="text-primary" />
                  Medical Notes
                </h2>
                <Button 
                  size="sm" 
                  variant="secondary"
                  onClick={() => setShowNotes(!showNotes)}
                >
                  Add Note
                </Button>
              </div>

              {showNotes && (
                <div className="mb-4">
                  <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Add a medical note..."
                    className="w-full bg-background border border-gray-800 rounded-lg p-3 focus:outline-none focus:border-primary"
                    rows="3"
                  />
                  <div className="flex justify-end gap-2 mt-2">
                    <Button size="sm" variant="secondary" onClick={() => setShowNotes(false)}>
                      Cancel
                    </Button>
                    <Button size="sm" onClick={handleAddNote}>
                      Save Note
                    </Button>
                  </div>
                </div>
              )}

              <div className="space-y-3">
                {claim.medicalNotes?.map((note, index) => (
                  <div key={index} className="bg-background/50 rounded-lg p-3">
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-medium text-sm">{note.author}</span>
                      <span className="text-xs text-textSecondary">
                        {note.date} {note.time}
                      </span>
                    </div>
                    <p className="text-sm text-textSecondary">{note.content}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column - Risk & Documents */}
          <div className="space-y-6">
            {/* Risk Score Card */}
            <div className="bg-surface rounded-xl border border-gray-800 p-6">
              <h2 className="text-lg font-bold mb-4">ML Risk Analysis</h2>
              <div className="flex justify-center mb-6">
                <RiskScore score={claim.risk} />
              </div>
              <LIMEExplanation factors={limeFactors} />
              
              {/* Priority Indicator */}
              {claim.priority === 'high' && (
                <div className="mt-4 p-3 bg-warning/10 border border-warning/30 rounded-lg">
                  <p className="text-warning text-sm flex items-center gap-2">
                    <FiAlertCircle />
                    High priority claim - requires immediate attention
                  </p>
                </div>
              )}
            </div>

            {/* Documents Card */}
            <div className="bg-surface rounded-xl border border-gray-800 p-6">
              <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                <FiFileText className="text-primary" />
                Documents
              </h2>
              
              <div className="space-y-3 mb-4">
                {claim.documents?.map((doc, index) => (
                  <div key={index} className="flex items-center justify-between bg-background p-3 rounded-lg">
                    <div className="flex items-center gap-3">
                      <FiFileText className="text-primary" />
                      <div>
                        <p className="text-sm">{doc.name}</p>
                        <p className="text-xs text-textSecondary">{doc.size}</p>
                      </div>
                    </div>
                    <button className="text-textSecondary hover:text-primary transition-colors">
                      <FiDownload />
                    </button>
                  </div>
                ))}
              </div>

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
                    <Button 
                      onClick={handleUpload}
                      disabled={uploading}
                      className="w-full"
                    >
                      {uploading ? 'Uploading...' : `Upload ${files.length} File(s)`}
                    </Button>
                  )}
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="bg-surface rounded-xl border border-gray-800 p-6">
              <h2 className="text-lg font-bold mb-4">Actions</h2>
              <div className="space-y-3">
                <Button className="w-full justify-center">
                  <FiEye className="mr-2" />
                  View Full Medical Records
                </Button>
                <Button variant="secondary" className="w-full justify-center">
                  <FiMessageSquare className="mr-2" />
                  Contact Insurance
                </Button>
                <Button variant="secondary" className="w-full justify-center">
                  <FiEdit className="mr-2" />
                  Edit Claim Details
                </Button>
              </div>
            </div>

            {/* Timeline */}
            <div className="bg-surface rounded-xl border border-gray-800 p-6">
              <h2 className="text-lg font-bold mb-4">Timeline</h2>
              <div className="space-y-3">
                <div className="flex gap-3">
                  <FiCheckCircle className="text-success flex-shrink-0 mt-1" />
                  <div>
                    <p className="text-sm font-medium">Submitted</p>
                    <p className="text-xs text-textSecondary">
                      {new Date(claim.submittedAt).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <FiClock className="text-warning flex-shrink-0 mt-1" />
                  <div>
                    <p className="text-sm font-medium">Last Updated</p>
                    <p className="text-xs text-textSecondary">
                      {new Date(claim.lastUpdated).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}