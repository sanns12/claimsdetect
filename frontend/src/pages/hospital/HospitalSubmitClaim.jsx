import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Button from '../../components/Button';
import FileUploader from '../../components/FileUploader';
import { 
  FiArrowLeft, 
  FiUploadCloud, 
  FiFileText, 
  FiUser, 
  FiCalendar, 
  FiDollarSign, 
  FiActivity,
  FiDownload,
  FiTrash2,
  FiPlus,
  FiAlertCircle,
  FiCheckCircle
} from 'react-icons/fi';
import { submitClaim } from '../../services/claims';
import { getRiskScore } from '../../services/risk';

export default function HospitalSubmitClaim() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('single'); // 'single' or 'bulk'
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');
  const [bulkFile, setBulkFile] = useState(null);
  const [bulkPreview, setBulkPreview] = useState([]);

  // Single claim form state
  const [formData, setFormData] = useState({
    patientId: '',
    patientName: '',
    age: '',
    gender: '',
    admissionDate: '',
    dischargeDate: '',
    diagnosis: '',
    procedure: '',
    amount: '',
    department: '',
    doctorName: '',
    insuranceProvider: '',
    policyNumber: ''
  });

  const [documents, setDocuments] = useState([]);
  const [errors, setErrors] = useState({});

  const departments = [
    'Select Department',
    'Emergency',
    'Cardiology',
    'Orthopedics',
    'Neurology',
    'Pediatrics',
    'Oncology',
    'Radiology',
    'Surgery',
    'ICU',
    'General Medicine'
  ];

  const diagnoses = [
    'Select Diagnosis',
    'Cardiovascular Disease',
    'Respiratory Infection',
    'Fracture',
    'Stroke',
    'Appendicitis',
    'Cancer',
    'Diabetes Complications',
    'Pneumonia',
    'COVID-19',
    'Other'
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  };

  const handleFileDrop = (acceptedFiles) => {
    setDocuments(prev => [...prev, ...acceptedFiles]);
  };

  const removeDocument = (index) => {
    setDocuments(prev => prev.filter((_, i) => i !== index));
  };

  const handleBulkFileDrop = (acceptedFiles) => {
    const file = acceptedFiles[0];
    setBulkFile(file);
    
    // Simulate parsing CSV/Excel preview
    setTimeout(() => {
      setBulkPreview([
        { id: 'P001', name: 'John Doe', amount: 5200, diagnosis: 'Cardiovascular', risk: 'Pending' },
        { id: 'P002', name: 'Jane Smith', amount: 12500, diagnosis: 'Orthopedic', risk: 'Pending' },
        { id: 'P003', name: 'Bob Johnson', amount: 3800, diagnosis: 'Respiratory', risk: 'Pending' },
        { id: 'P004', name: 'Alice Brown', amount: 8900, diagnosis: 'Neurology', risk: 'Pending' },
      ]);
    }, 1000);
  };

  const validateForm = () => {
    const newErrors = {};
    const requiredFields = [
      'patientId', 'patientName', 'age', 'admissionDate', 
      'diagnosis', 'amount', 'department', 'insuranceProvider'
    ];
    
    requiredFields.forEach(field => {
      if (!formData[field]) {
        newErrors[field] = `${field.replace(/([A-Z])/g, ' $1').toLowerCase()} is required`;
      }
    });

    if (formData.diagnosis === 'Select Diagnosis') {
      newErrors.diagnosis = 'Please select a diagnosis';
    }

    if (formData.department === 'Select Department') {
      newErrors.department = 'Please select a department';
    }

    if (formData.admissionDate && formData.dischargeDate) {
      if (new Date(formData.dischargeDate) < new Date(formData.admissionDate)) {
        newErrors.dischargeDate = 'Discharge date must be after admission date';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const calculateRiskForBulk = async () => {
    const updatedPreview = await Promise.all(
      bulkPreview.map(async (item) => {
        const riskData = await getRiskScore({
          amount: item.amount,
          diagnosis: item.diagnosis,
          age: 45 // Default age for preview
        });
        return { ...item, risk: riskData.score };
      })
    );
    setBulkPreview(updatedPreview);
  };

  const handleSingleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setIsSubmitting(true);
    setSubmitError('');

    try {
      // Get ML risk score
      const riskData = await getRiskScore({
        age: parseInt(formData.age),
        amount: parseFloat(formData.amount),
        diagnosis: formData.diagnosis,
        admissionDate: formData.admissionDate,
        dischargeDate: formData.dischargeDate
      });

      const claimData = {
        ...formData,
        hospitalId: 'HOSP-001', // From hospital profile
        hospitalName: 'City General Hospital',
        submittedBy: 'Dr. Smith',
        riskScore: riskData.score,
        riskFactors: riskData.factors,
        status: riskData.score > 70 ? 'Flagged' : 'Submitted',
        submittedAt: new Date().toISOString()
      };

      const result = await submitClaim(claimData, documents);
      
      navigate('/hospital/claims', { 
        state: { 
          message: 'Claim submitted successfully!',
          claimId: result.claimId
        } 
      });
    } catch (error) {
      setSubmitError(error.message || 'Failed to submit claim');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleBulkSubmit = async () => {
    setIsSubmitting(true);
    setSubmitError('');

    try {
      await calculateRiskForBulk();
      
      // Submit each claim
      for (const item of bulkPreview) {
        await submitClaim({
          patientId: item.id,
          patientName: item.name,
          amount: item.amount,
          diagnosis: item.diagnosis,
          hospitalId: 'HOSP-001',
          submittedAt: new Date().toISOString()
        }, []);
      }
      
      navigate('/hospital/claims', { 
        state: { 
          message: `${bulkPreview.length} claims submitted successfully!`,
          type: 'success'
        } 
      });
    } catch {
      setSubmitError('Bulk submission failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-white">
      {/* Header */}
      <header className="bg-surface/50 backdrop-blur-sm border-b border-gray-800 sticky top-0 z-50">
        <div className="px-6 py-4 flex items-center gap-4">
          <Link 
            to="/hospital/dashboard" 
            className="p-2 hover:bg-surface rounded-lg transition-colors"
          >
            <FiArrowLeft className="text-xl" />
          </Link>
          <h1 className="text-xl font-bold">Submit Claim</h1>
          <span className="text-sm bg-primary/20 text-primary px-3 py-1 rounded-full ml-4">
            City General Hospital
          </span>
        </div>
      </header>

      {/* Tabs */}
      <div className="px-6 pt-6">
        <div className="flex gap-4 border-b border-gray-800">
          <button
            onClick={() => setActiveTab('single')}
            className={`px-4 py-2 font-medium transition-colors relative ${
              activeTab === 'single' 
                ? 'text-primary' 
                : 'text-textSecondary hover:text-white'
            }`}
          >
            Single Claim
            {activeTab === 'single' && (
              <div className="absolute bottom-0 left-0 w-full h-0.5 bg-primary"></div>
            )}
          </button>
          <button
            onClick={() => setActiveTab('bulk')}
            className={`px-4 py-2 font-medium transition-colors relative ${
              activeTab === 'bulk' 
                ? 'text-primary' 
                : 'text-textSecondary hover:text-white'
            }`}
          >
            Bulk Upload
            {activeTab === 'bulk' && (
              <div className="absolute bottom-0 left-0 w-full h-0.5 bg-primary"></div>
            )}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <main className="p-6">
        {activeTab === 'single' ? (
          /* Single Claim Form */
          <form onSubmit={handleSingleSubmit} className="max-w-4xl mx-auto">
            {/* Error Message */}
            {submitError && (
              <div className="mb-6 bg-danger/10 border border-danger/30 text-danger px-4 py-3 rounded-lg flex items-center gap-3">
                <FiAlertCircle />
                {submitError}
              </div>
            )}

            {/* Patient Information */}
            <div className="bg-surface rounded-xl border border-gray-800 p-6 mb-6">
              <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                <FiUser className="text-primary" />
                Patient Information
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Patient ID</label>
                  <input
                    type="text"
                    name="patientId"
                    value={formData.patientId}
                    onChange={handleChange}
                    className={`w-full bg-background border rounded-lg py-2 px-3 focus:outline-none focus:border-primary ${
                      errors.patientId ? 'border-danger' : 'border-gray-800'
                    }`}
                    placeholder="e.g., P001234"
                  />
                  {errors.patientId && (
                    <p className="text-danger text-xs mt-1">{errors.patientId}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Full Name</label>
                  <input
                    type="text"
                    name="patientName"
                    value={formData.patientName}
                    onChange={handleChange}
                    className={`w-full bg-background border rounded-lg py-2 px-3 focus:outline-none focus:border-primary ${
                      errors.patientName ? 'border-danger' : 'border-gray-800'
                    }`}
                    placeholder="Enter patient name"
                  />
                  {errors.patientName && (
                    <p className="text-danger text-xs mt-1">{errors.patientName}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Age</label>
                  <input
                    type="number"
                    name="age"
                    value={formData.age}
                    onChange={handleChange}
                    className={`w-full bg-background border rounded-lg py-2 px-3 focus:outline-none focus:border-primary ${
                      errors.age ? 'border-danger' : 'border-gray-800'
                    }`}
                    placeholder="Age"
                    min="0"
                    max="120"
                  />
                  {errors.age && (
                    <p className="text-danger text-xs mt-1">{errors.age}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Gender</label>
                  <select
                    name="gender"
                    value={formData.gender}
                    onChange={handleChange}
                    className="w-full bg-background border border-gray-800 rounded-lg py-2 px-3 focus:outline-none focus:border-primary"
                  >
                    <option value="">Select Gender</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Claim Details */}
            <div className="bg-surface rounded-xl border border-gray-800 p-6 mb-6">
              <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                <FiActivity className="text-primary" />
                Claim Details
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Admission Date</label>
                  <input
                    type="date"
                    name="admissionDate"
                    value={formData.admissionDate}
                    onChange={handleChange}
                    className={`w-full bg-background border rounded-lg py-2 px-3 focus:outline-none focus:border-primary ${
                      errors.admissionDate ? 'border-danger' : 'border-gray-800'
                    }`}
                  />
                  {errors.admissionDate && (
                    <p className="text-danger text-xs mt-1">{errors.admissionDate}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Discharge Date</label>
                  <input
                    type="date"
                    name="dischargeDate"
                    value={formData.dischargeDate}
                    onChange={handleChange}
                    className={`w-full bg-background border rounded-lg py-2 px-3 focus:outline-none focus:border-primary ${
                      errors.dischargeDate ? 'border-danger' : 'border-gray-800'
                    }`}
                  />
                  {errors.dischargeDate && (
                    <p className="text-danger text-xs mt-1">{errors.dischargeDate}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Diagnosis</label>
                  <select
                    name="diagnosis"
                    value={formData.diagnosis}
                    onChange={handleChange}
                    className={`w-full bg-background border rounded-lg py-2 px-3 focus:outline-none focus:border-primary ${
                      errors.diagnosis ? 'border-danger' : 'border-gray-800'
                    }`}
                  >
                    {diagnoses.map(d => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                  {errors.diagnosis && (
                    <p className="text-danger text-xs mt-1">{errors.diagnosis}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Procedure</label>
                  <input
                    type="text"
                    name="procedure"
                    value={formData.procedure}
                    onChange={handleChange}
                    className="w-full bg-background border border-gray-800 rounded-lg py-2 px-3 focus:outline-none focus:border-primary"
                    placeholder="e.g., Appendectomy"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Department</label>
                  <select
                    name="department"
                    value={formData.department}
                    onChange={handleChange}
                    className={`w-full bg-background border rounded-lg py-2 px-3 focus:outline-none focus:border-primary ${
                      errors.department ? 'border-danger' : 'border-gray-800'
                    }`}
                  >
                    {departments.map(d => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                  {errors.department && (
                    <p className="text-danger text-xs mt-1">{errors.department}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Attending Doctor</label>
                  <input
                    type="text"
                    name="doctorName"
                    value={formData.doctorName}
                    onChange={handleChange}
                    className="w-full bg-background border border-gray-800 rounded-lg py-2 px-3 focus:outline-none focus:border-primary"
                    placeholder="Dr. Name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Claim Amount ($)</label>
                  <input
                    type="number"
                    name="amount"
                    value={formData.amount}
                    onChange={handleChange}
                    className={`w-full bg-background border rounded-lg py-2 px-3 focus:outline-none focus:border-primary ${
                      errors.amount ? 'border-danger' : 'border-gray-800'
                    }`}
                    placeholder="Enter amount"
                    min="0"
                    step="0.01"
                  />
                  {errors.amount && (
                    <p className="text-danger text-xs mt-1">{errors.amount}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Insurance Information */}
            <div className="bg-surface rounded-xl border border-gray-800 p-6 mb-6">
              <h2 className="text-lg font-bold mb-4">Insurance Information</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Insurance Provider</label>
                  <input
                    type="text"
                    name="insuranceProvider"
                    value={formData.insuranceProvider}
                    onChange={handleChange}
                    className={`w-full bg-background border rounded-lg py-2 px-3 focus:outline-none focus:border-primary ${
                      errors.insuranceProvider ? 'border-danger' : 'border-gray-800'
                    }`}
                    placeholder="e.g., Blue Cross"
                  />
                  {errors.insuranceProvider && (
                    <p className="text-danger text-xs mt-1">{errors.insuranceProvider}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Policy Number</label>
                  <input
                    type="text"
                    name="policyNumber"
                    value={formData.policyNumber}
                    onChange={handleChange}
                    className="w-full bg-background border border-gray-800 rounded-lg py-2 px-3 focus:outline-none focus:border-primary"
                    placeholder="Policy #"
                  />
                </div>
              </div>
            </div>

            {/* Documents */}
            <div className="bg-surface rounded-xl border border-gray-800 p-6 mb-6">
              <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                <FiFileText className="text-primary" />
                Supporting Documents
              </h2>
              
              <FileUploader onDrop={handleFileDrop} />

              {documents.length > 0 && (
                <div className="mt-4 space-y-2">
                  {documents.map((file, index) => (
                    <div key={index} className="flex items-center justify-between bg-background p-3 rounded-lg">
                      <div className="flex items-center gap-3">
                        <FiFileText className="text-primary" />
                        <span className="text-sm">{file.name}</span>
                        <span className="text-xs text-textSecondary">
                          ({(file.size / 1024).toFixed(2)} KB)
                        </span>
                      </div>
                      <button
                        type="button"
                        onClick={() => removeDocument(index)}
                        className="text-danger hover:text-danger/80"
                      >
                        <FiTrash2 />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Submit Button */}
            <div className="flex justify-end gap-4">
              <Button 
                type="button" 
                variant="secondary"
                onClick={() => navigate('/hospital/dashboard')}
              >
                Cancel
              </Button>
              <Button 
                type="submit" 
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Submitting...' : 'Submit Claim for ML Review'}
              </Button>
            </div>
          </form>
        ) : (
          /* Bulk Upload */
          <div className="max-w-4xl mx-auto">
            <div className="bg-surface rounded-xl border border-gray-800 p-6 mb-6">
              <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                <FiUploadCloud className="text-primary" />
                Bulk Upload Claims
              </h2>
              
              <p className="text-textSecondary text-sm mb-4">
                Upload a CSV or Excel file with multiple claims. 
                <a href="#" className="text-primary ml-2 hover:underline">
                  Download template
                </a>
              </p>

              <FileUploader onDrop={handleBulkFileDrop} />

              {bulkFile && (
                <div className="mt-4 p-3 bg-background rounded-lg flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <FiFileText className="text-primary" />
                    <span>{bulkFile.name}</span>
                  </div>
                  <FiCheckCircle className="text-success" />
                </div>
              )}
            </div>

            {/* Bulk Preview */}
            {bulkPreview.length > 0 && (
              <div className="bg-surface rounded-xl border border-gray-800 p-6 mb-6">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="font-bold">Preview ({bulkPreview.length} claims)</h2>
                  <Button 
                    size="sm" 
                    onClick={calculateRiskForBulk}
                  >
                    Calculate Risk Scores
                  </Button>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-background/50">
                      <tr className="text-left text-textSecondary text-sm">
                        <th className="px-4 py-2">Patient ID</th>
                        <th className="px-4 py-2">Name</th>
                        <th className="px-4 py-2">Amount</th>
                        <th className="px-4 py-2">Diagnosis</th>
                        <th className="px-4 py-2">Risk Score</th>
                      </tr>
                    </thead>
                    <tbody>
                      {bulkPreview.map((item, index) => (
                        <tr key={index} className="border-t border-gray-800">
                          <td className="px-4 py-3">{item.id}</td>
                          <td className="px-4 py-3">{item.name}</td>
                          <td className="px-4 py-3">${item.amount}</td>
                          <td className="px-4 py-3">{item.diagnosis}</td>
                          <td className="px-4 py-3">
                            {item.risk !== 'Pending' ? (
                              <span className={`px-2 py-1 rounded-full text-xs ${
                                item.risk > 70 ? 'bg-danger/20 text-danger' :
                                item.risk > 40 ? 'bg-warning/20 text-warning' :
                                'bg-success/20 text-success'
                              }`}>
                                {item.risk}%
                              </span>
                            ) : (
                              <span className="text-textSecondary">Pending</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Submit Bulk */}
            {bulkPreview.length > 0 && (
              <div className="flex justify-end gap-4">
                <Button 
                  type="button" 
                  variant="secondary"
                  onClick={() => {
                    setBulkFile(null);
                    setBulkPreview([]);
                  }}
                >
                  Clear
                </Button>
                <Button 
                  onClick={handleBulkSubmit}
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Submitting...' : `Submit ${bulkPreview.length} Claims`}
                </Button>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}