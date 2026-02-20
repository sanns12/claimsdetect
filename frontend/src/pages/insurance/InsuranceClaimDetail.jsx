import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import Button from '../../components/Button';
import StatusBadge from '../../components/StatusBadge';
import RiskScore from '../../components/RiskScore';
import LIMEExplanation from '../../components/LIMEExplanation';
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
  FiXCircle,
  FiLoader,
  FiRefreshCw,
  FiShield,
  FiFlag,
  FiThumbsUp,
  FiThumbsDown,
  FiEye,
  FiPrinter,
  FiMessageSquare,
  FiBarChart2,
  FiUsers,
  FiHome
} from 'react-icons/fi';
import { CLAIM_STATUS } from '../../utils/constants';

export default function InsuranceClaimDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionInProgress, setActionInProgress] = useState(false);
  const [showDecisionModal, setShowDecisionModal] = useState(false);
  const [decision, setDecision] = useState(null);
  const [decisionNotes, setDecisionNotes] = useState('');
  const [limeFactors, setLimeFactors] = useState([]);
  const [similarClaims, setSimilarClaims] = useState([]);

  // Load claim data directly in useEffect - NO separate function
  useEffect(() => {
    // Mock data - replace with API call
    setTimeout(() => {
      const mockClaim = {
        id: id,
        patientId: 'P100234',
        patientName: 'Sarah Johnson',
        age: 45,
        gender: 'Female',
        date: '2024-03-20',
        amount: 15200,
        status: CLAIM_STATUS.FLAGGED,
        risk: 76,
        fraudScore: 0.78,
        department: 'Cardiology',
        diagnosis: 'Cardiovascular Disease',
        procedure: 'Angioplasty',
        hospital: 'City General Hospital',
        hospitalId: 'HOSP-001',
        hospitalAddress: '123 Main St, New York, NY 10001',
        doctor: 'Dr. Williams',
        doctorLicense: 'MD12345',
        insuranceProvider: 'Blue Cross',
        policyNumber: 'BC-789012',
        groupNumber: 'GRP-456',
        admissionDate: '2024-03-15',
        dischargeDate: '2024-03-18',
        stayDuration: '3 days',
        documents: [
          { name: 'admission_form.pdf', size: '245 KB', type: 'PDF' },
          { name: 'lab_results.pdf', size: '1.2 MB', type: 'PDF' },
          { name: 'discharge_summary.pdf', size: '892 KB', type: 'PDF' },
          { name: 'xray_image.jpg', size: '3.1 MB', type: 'Image' }
        ],
        flags: [
          { type: 'Amount Anomaly', severity: 'high', description: 'Amount 45% above average for this procedure' },
          { type: 'Hospital History', severity: 'medium', description: 'Hospital has 3 flagged claims this month' },
          { type: 'Pattern Match', severity: 'high', description: 'Matches fraud pattern #F123' }
        ],
        fraudIndicators: [
          { name: 'Amount vs Average', value: '+45%', risk: 'high' },
          { name: 'Length of Stay', value: '-2 days', risk: 'medium' },
          { name: 'Duplicate Codes', value: 'None', risk: 'low' },
          { name: 'Provider History', value: '3 flags', risk: 'high' }
        ],
        submittedBy: 'Dr. Williams',
        submittedAt: '2024-03-20T10:30:00',
        lastUpdated: '2024-03-20T14:25:00',
        priority: 'high',
        assignedTo: 'John Smith',
        reviewHistory: [
          { action: 'AI Flagged', date: '2024-03-20 10:35', by: 'ML Model', reason: 'Amount anomaly detected' },
          { action: 'Assigned', date: '2024-03-20 11:00', by: 'System', reason: 'Auto-assigned to John Smith' }
        ]
      };
      
      setClaim(mockClaim);

      setLimeFactors([
        { 
          name: 'Claim Amount', 
          impact: 42, 
          color: 'high',
          description: 'Amount 45% above average for angioplasty'
        },
        { 
          name: 'Hospital Risk Score', 
          impact: 28, 
          color: 'medium',
          description: 'Hospital has elevated risk profile'
        },
        { 
          name: 'Length of Stay', 
          impact: 18, 
          color: 'low',
          description: 'Stay duration shorter than typical'
        },
        { 
          name: 'Procedure Code', 
          impact: 12, 
          color: 'low',
          description: 'Standard procedure with normal patterns'
        }
      ]);

      setSimilarClaims([
        { id: 'CLM2340', amount: 14800, status: CLAIM_STATUS.FRAUD, similarity: '94%', date: '2024-03-15' },
        { id: 'CLM2321', amount: 16100, status: CLAIM_STATUS.FRAUD, similarity: '89%', date: '2024-03-10' },
        { id: 'CLM2298', amount: 13900, status: CLAIM_STATUS.FLAGGED, similarity: '82%', date: '2024-03-05' }
      ]);

      setLoading(false);
    }, 1000);
  }, [id]); // Only depends on id

  // Refresh handler - direct function
  const handleRefresh = () => {
    // Mock data - replace with API call
    setTimeout(() => {
      const mockClaim = {
        id: id,
        patientId: 'P100234',
        patientName: 'Sarah Johnson',
        age: 45,
        gender: 'Female',
        date: '2024-03-20',
        amount: 15200,
        status: CLAIM_STATUS.FLAGGED,
        risk: 76,
        fraudScore: 0.78,
        department: 'Cardiology',
        diagnosis: 'Cardiovascular Disease',
        procedure: 'Angioplasty',
        hospital: 'City General Hospital',
        hospitalId: 'HOSP-001',
        hospitalAddress: '123 Main St, New York, NY 10001',
        doctor: 'Dr. Williams',
        doctorLicense: 'MD12345',
        insuranceProvider: 'Blue Cross',
        policyNumber: 'BC-789012',
        groupNumber: 'GRP-456',
        admissionDate: '2024-03-15',
        dischargeDate: '2024-03-18',
        stayDuration: '3 days',
        documents: [
          { name: 'admission_form.pdf', size: '245 KB', type: 'PDF' },
          { name: 'lab_results.pdf', size: '1.2 MB', type: 'PDF' },
          { name: 'discharge_summary.pdf', size: '892 KB', type: 'PDF' },
          { name: 'xray_image.jpg', size: '3.1 MB', type: 'Image' }
        ],
        flags: [
          { type: 'Amount Anomaly', severity: 'high', description: 'Amount 45% above average for this procedure' },
          { type: 'Hospital History', severity: 'medium', description: 'Hospital has 3 flagged claims this month' },
          { type: 'Pattern Match', severity: 'high', description: 'Matches fraud pattern #F123' }
        ],
        fraudIndicators: [
          { name: 'Amount vs Average', value: '+45%', risk: 'high' },
          { name: 'Length of Stay', value: '-2 days', risk: 'medium' },
          { name: 'Duplicate Codes', value: 'None', risk: 'low' },
          { name: 'Provider History', value: '3 flags', risk: 'high' }
        ],
        submittedBy: 'Dr. Williams',
        submittedAt: '2024-03-20T10:30:00',
        lastUpdated: '2024-03-20T14:25:00',
        priority: 'high',
        assignedTo: 'John Smith',
        reviewHistory: [
          { action: 'AI Flagged', date: '2024-03-20 10:35', by: 'ML Model', reason: 'Amount anomaly detected' },
          { action: 'Assigned', date: '2024-03-20 11:00', by: 'System', reason: 'Auto-assigned to John Smith' }
        ]
      };
      
      setClaim(mockClaim);
      setLoading(false);
    }, 1000);
  };

  const handleDecision = (action) => {
    setDecision(action);
    setShowDecisionModal(true);
  };

  const confirmDecision = () => {
    setActionInProgress(true);
    
    setTimeout(() => {
      setActionInProgress(false);
      setShowDecisionModal(false);
      
      const updatedClaim = { ...claim };
      if (decision === 'approve') updatedClaim.status = CLAIM_STATUS.APPROVED;
      if (decision === 'flag') updatedClaim.status = CLAIM_STATUS.FLAGGED;
      if (decision === 'fraud') updatedClaim.status = CLAIM_STATUS.FRAUD;
      
      setClaim(updatedClaim);
      
      setTimeout(() => {
        navigate('/insurance/claims', { 
          state: { 
            message: `Claim ${decision === 'approve' ? 'approved' : decision === 'flag' ? 'flagged' : 'marked as fraud'} successfully`
          } 
        });
      }, 1500);
    }, 2000);
  };
  if (loading) return <div className="flex items-center justify-center h-screen"><FiLoader className="animate-spin text-2xl" /></div>;
  if (!claim) return <div className="text-center py-8">No Claim Found</div>;

  return (
    <div className="space-y-6 pb-8">
      {/* Header */}
      <div className="flex items-center justify-between border-b pb-4">
        <div>
          <Link to="/insurance/claims" className="flex items-center text-blue-600 hover:text-blue-800 mb-4">
            <FiArrowLeft className="mr-2" /> Back to Claims
          </Link>
          <h1 className="text-3xl font-bold">Claim Details</h1>
          <p className="text-gray-600">Claim ID: {claim.id}</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleRefresh} className="flex items-center gap-2" variant="secondary">
            <FiRefreshCw /> Refresh
          </Button>
        </div>
      </div>

      {/* Status Bar */}
      <div className="bg-white rounded-lg shadow p-4 border-l-4 border-yellow-500">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-gray-600">Status</p>
            <StatusBadge status={claim.status} />
          </div>
          <div>
            <p className="text-sm text-gray-600">Risk Score</p>
            <RiskScore score={claim.risk} />
          </div>
          <div>
            <p className="text-sm text-gray-600">Fraud Score</p>
            <p className="text-2xl font-bold text-red-600">{(claim.fraudScore * 100).toFixed(0)}%</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Priority</p>
            <p className={`font-bold ${claim.priority === 'high' ? 'text-red-600' : 'text-yellow-600'}`}>{claim.priority.toUpperCase()}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Patient Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><FiUser /> Patient Information</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-600">Patient Name</p>
                <p className="font-semibold">{claim.patientName}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Patient ID</p>
                <p className="font-semibold">{claim.patientId}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Age</p>
                <p className="font-semibold">{claim.age}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Gender</p>
                <p className="font-semibold">{claim.gender}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Admission Date</p>
                <p className="font-semibold flex items-center gap-1"><FiCalendar className="text-sm" /> {claim.admissionDate}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Discharge Date</p>
                <p className="font-semibold flex items-center gap-1"><FiCalendar className="text-sm" /> {claim.dischargeDate}</p>
              </div>
            </div>
          </div>

          {/* Medical Details */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><FiActivity /> Medical Details</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Department</p>
                <p className="font-semibold">{claim.department}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Procedure</p>
                <p className="font-semibold">{claim.procedure}</p>
              </div>
              <div className="col-span-2">
                <p className="text-sm text-gray-600">Diagnosis</p>
                <p className="font-semibold">{claim.diagnosis}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Doctor</p>
                <p className="font-semibold">{claim.doctor}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">License</p>
                <p className="font-semibold text-xs">{claim.doctorLicense}</p>
              </div>
            </div>
          </div>

          {/* Claim Amount & Insurance */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><FiDollarSign /> Claim & Insurance Details</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-600">Claim Amount</p>
                <p className="text-2xl font-bold text-green-600">${claim.amount.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Stay Duration</p>
                <p className="font-semibold">{claim.stayDuration}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Insurance Provider</p>
                <p className="font-semibold">{claim.insuranceProvider}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Policy Number</p>
                <p className="font-semibold text-xs">{claim.policyNumber}</p>
              </div>
              <div className="col-span-2">
                <p className="text-sm text-gray-600">Group Number</p>
                <p className="font-semibold">{claim.groupNumber}</p>
              </div>
            </div>
          </div>

          {/* Hospital Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><FiHome /> Hospital Information</h2>
            <div>
              <p className="text-sm text-gray-600">Hospital Name</p>
              <p className="font-semibold mb-3">{claim.hospital}</p>
              <p className="text-sm text-gray-600">Hospital ID</p>
              <p className="font-semibold mb-3">{claim.hospitalId}</p>
              <p className="text-sm text-gray-600">Address</p>
              <p className="font-semibold">{claim.hospitalAddress}</p>
            </div>
          </div>

          {/* Fraud Indicators */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><FiAlertCircle /> Fraud Indicators</h2>
            <div className="space-y-3">
              {claim.fraudIndicators.map((indicator, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 border rounded">
                  <span className="font-semibold">{indicator.name}</span>
                  <div className="flex items-center gap-3">
                    <span className="font-semibold">{indicator.value}</span>
                    <span className={`px-3 py-1 rounded text-xs font-bold ${
                      indicator.risk === 'high' ? 'bg-red-100 text-red-800' :
                      indicator.risk === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {indicator.risk.toUpperCase()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Flags */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><FiFlag /> Alerts & Flags</h2>
            <div className="space-y-3">
              {claim.flags.map((flag, idx) => (
                <div key={idx} className={`p-4 border-l-4 rounded ${
                  flag.severity === 'high' ? 'border-red-500 bg-red-50' :
                  'border-yellow-500 bg-yellow-50'
                }`}>
                  <div className="flex items-start gap-3">
                    {flag.severity === 'high' ? <FiAlertCircle className="text-red-600 mt-1" /> : <FiFlag className="text-yellow-600 mt-1" />}
                    <div>
                      <p className="font-bold">{flag.type}</p>
                      <p className="text-sm text-gray-700">{flag.description}</p>
                      <span className={`inline-block mt-2 px-3 py-1 rounded text-xs font-bold ${
                        flag.severity === 'high' ? 'bg-red-200 text-red-800' : 'bg-yellow-200 text-yellow-800'
                      }`}>
                        {flag.severity.toUpperCase()} SEVERITY
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Documents */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><FiFileText /> Attached Documents</h2>
            <div className="space-y-2">
              {claim.documents.map((doc, idx) => (
                <div key={idx} className="flex items-center justify-between p-3 border rounded hover:bg-gray-50">
                  <div className="flex items-center gap-3">
                    <FiDownload className="text-blue-600" />
                    <div>
                      <p className="font-semibold">{doc.name}</p>
                      <p className="text-sm text-gray-600">{doc.type} • {doc.size}</p>
                    </div>
                  </div>
                  <Button variant="secondary" className="text-sm">Download</Button>
                </div>
              ))}
            </div>
          </div>

          {/* Review History */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><FiClock /> Review History</h2>
            <div className="space-y-4">
              {claim.reviewHistory.map((review, idx) => (
                <div key={idx} className="flex gap-4 pb-4 border-b last:border-b-0">
                  <div className="text-sm font-semibold text-gray-500 min-w-[80px]">{review.date}</div>
                  <div>
                    <p className="font-bold">{review.action}</p>
                    <p className="text-sm text-gray-600">By: {review.by}</p>
                    <p className="text-sm text-gray-600">{review.reason}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* LIME Explanation */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><FiBarChart2 /> Risk Factors</h2>
            <LIMEExplanation factors={limeFactors} />
          </div>

          {/* Assignment */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2"><FiUsers /> Assignment</h2>
            <div>
              <p className="text-sm text-gray-600">Assigned To</p>
              <p className="font-semibold mb-3">{claim.assignedTo}</p>
              <p className="text-sm text-gray-600">Submitted By</p>
              <p className="font-semibold mb-3">{claim.submittedBy}</p>
              <p className="text-sm text-gray-600">Submitted At</p>
              <p className="font-semibold text-xs">{new Date(claim.submittedAt).toLocaleString()}</p>
            </div>
          </div>

          {/* Similar Claims */}
          {similarClaims.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-bold mb-4 flex items-center gap-2"><FiEye /> Similar Claims</h2>
              <div className="space-y-3">
                {similarClaims.map((sim, idx) => (
                  <div key={idx} className="p-3 border rounded hover:bg-gray-50 cursor-pointer">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-bold text-sm">{sim.id}</p>
                        <p className="text-xs text-gray-600">${sim.amount.toLocaleString()}</p>
                      </div>
                      <span className="text-xs font-bold text-blue-600">{sim.similarity}</span>
                    </div>
                    <div className="mt-2">
                      <StatusBadge status={sim.status} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-bold mb-4">Actions</h2>
            <div className="space-y-2">
              <Button 
                onClick={() => handleDecision('approve')} 
                className="w-full flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700"
                disabled={actionInProgress}
              >
                <FiThumbsUp /> Approve
              </Button>
              <Button 
                onClick={() => handleDecision('flag')} 
                className="w-full flex items-center justify-center gap-2 bg-yellow-600 hover:bg-yellow-700"
                disabled={actionInProgress}
              >
                <FiFlag /> Flag for Review
              </Button>
              <Button 
                onClick={() => handleDecision('fraud')} 
                className="w-full flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700"
                disabled={actionInProgress}
              >
                <FiThumbsDown /> Mark as Fraud
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Decision Modal */}
      {showDecisionModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold mb-4">
              {decision === 'approve' && 'Approve Claim?'}
              {decision === 'flag' && 'Flag for Review?'}
              {decision === 'fraud' && 'Mark as Fraud?'}
            </h3>
            
            <textarea
              value={decisionNotes}
              onChange={(e) => setDecisionNotes(e.target.value)}
              placeholder="Add notes (optional)"
              className="w-full p-3 border rounded-lg mb-4 resize-none"
              rows="4"
            />
            
            <div className="flex gap-3">
              <Button 
                onClick={() => { setShowDecisionModal(false); setDecisionNotes(''); }}
                variant="secondary"
                className="flex-1"
              >
                Cancel
              </Button>
              <Button 
                onClick={confirmDecision}
                className={`flex-1 ${
                  decision === 'approve' ? 'bg-green-600 hover:bg-green-700' :
                  decision === 'flag' ? 'bg-yellow-600 hover:bg-yellow-700' :
                  'bg-red-600 hover:bg-red-700'
                }`}
                disabled={actionInProgress}
              >
                {actionInProgress ? <FiLoader className="animate-spin" /> : 'Confirm'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}