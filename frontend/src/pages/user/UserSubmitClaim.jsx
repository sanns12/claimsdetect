import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Button from '../../components/Button';
import FileUploader from '../../components/FileUploader';
import { FiArrowLeft, FiCalendar, FiDollarSign, FiUser, FiActivity, FiFileText, FiAlertCircle } from 'react-icons/fi';
import { submitClaim } from '../../services/claims';


export default function UserSubmitClaim() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    fullName: '',
    age: '',
    admissionDate: '',
    dischargeDate: '',
    disease: '',
    amount: '',
  });
  
  const [files, setFiles] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [errors, setErrors] = useState({});
  const [submitError, setSubmitError] = useState('');
  

  const diseases = [
    'Select Disease',
    'Cardiovascular',
    'Respiratory',
    'Orthopedic',
    'Neurological',
    'Gastrointestinal',
    'Infectious Disease',
    'Oncology',
    'Other'
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
    // Reset ML risk score when form changes
    //setMlRiskScore(null);
  };

  const handleFileDrop = (acceptedFiles) => {
    setFiles(prev => [...prev, ...acceptedFiles]);
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const validateStep1 = () => {
    const newErrors = {};
    if (!formData.fullName) newErrors.fullName = 'Full name is required';
    if (!formData.age) newErrors.age = 'Age is required';
    else if (formData.age < 0 || formData.age > 120) newErrors.age = 'Please enter a valid age';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep2 = () => {
    const newErrors = {};
    if (!formData.admissionDate) newErrors.admissionDate = 'Admission date is required';
    if (!formData.dischargeDate) newErrors.dischargeDate = 'Discharge date is required';
    if (!formData.disease || formData.disease === 'Select Disease') newErrors.disease = 'Please select a disease';
    if (!formData.amount) newErrors.amount = 'Claim amount is required';
    else if (formData.amount <= 0) newErrors.amount = 'Amount must be greater than 0';
    
    // Check if discharge date is after admission date
    if (formData.admissionDate && formData.dischargeDate) {
      if (new Date(formData.dischargeDate) < new Date(formData.admissionDate)) {
        newErrors.dischargeDate = 'Discharge date must be after admission date';
      }
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };


  const nextStep = async () => {
    if (currentStep === 1 && validateStep1()) {
      setCurrentStep(2);
    } else if (currentStep === 2 && validateStep2()) {
      
      setCurrentStep(3);
    }
  };

  const prevStep = () => {
    setCurrentStep(currentStep - 1);
    // Clear step-specific errors when going back
    setErrors({});
  };

  const handleSubmit = async (e) => {
  e.preventDefault();

  if (currentStep === 3) {
    setIsSubmitting(true);
    setSubmitError('');

    try {
      const claimData = {
        age: parseInt(formData.age),
        disease: formData.disease,
        admission_date: formData.admissionDate,
        discharge_date: formData.dischargeDate,
        claim_amount: parseFloat(formData.amount),
        patient_name: formData.fullName,
        hospital_name: 'City General Hospital',
        gender: "M" // or add gender field later properly
      };

      const result = await submitClaim(claimData, files[0]);

      navigate('/user/claims', {
        state: {
          message: "Claim submitted successfully!",
          claimId: result.claimId
        }
      });

    } catch (error) {
      setSubmitError(error.message || 'Failed to submit claim.');
    } finally {
      setIsSubmitting(false);
    }
  }
};
  // Calculate stay duration for display
  const getStayDuration = () => {
    if (formData.admissionDate && formData.dischargeDate) {
      const start = new Date(formData.admissionDate);
      const end = new Date(formData.dischargeDate);
      const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24));
      return days > 0 ? `${days} days` : 'Same day';
    }
    return null;
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800/50 backdrop-blur-sm border-b border-gray-800 sticky top-0 z-50">
        <div className="px-6 py-4 flex items-center gap-4">
          <Link 
            to="/user/dashboard" 
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <FiArrowLeft className="text-xl" />
          </Link>
          <h1 className="text-xl font-bold">Submit New Claim</h1>
        </div>
      </header>

      {/* Progress Bar */}
      <div className="px-6 pt-6">
        <div className="flex items-center justify-between max-w-3xl mx-auto">
          <div className="flex items-center flex-1">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
              currentStep >= 1 ? 'bg-blue-600' : 'bg-gray-700'
            }`}>
              1
            </div>
            <div className={`flex-1 h-1 mx-2 ${
              currentStep >= 2 ? 'bg-blue-600' : 'bg-gray-700'
            }`}></div>
          </div>
          <div className="flex items-center flex-1">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
              currentStep >= 2 ? 'bg-blue-600' : 'bg-gray-700'
            }`}>
              2
            </div>
            <div className={`flex-1 h-1 mx-2 ${
              currentStep >= 3 ? 'bg-blue-600' : 'bg-gray-700'
            }`}></div>
          </div>
          <div className="flex items-center">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
              currentStep >= 3 ? 'bg-blue-600' : 'bg-gray-700'
            }`}>
              3
            </div>
          </div>
        </div>
        <div className="flex justify-between max-w-3xl mx-auto mt-2 text-sm text-gray-400">
          <span>Personal Info</span>
          <span>Claim Details</span>
          <span>Documents & Review</span>
        </div>
      </div>

      {/* Main Form */}
      <main className="p-6">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
          {/* Step 1: Personal Information */}
          {currentStep === 1 && (
            <div className="space-y-6">
              <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <FiUser className="text-blue-500" />
                  Personal Information
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium mb-2">Full Name</label>
                    <input
                      type="text"
                      name="fullName"
                      value={formData.fullName}
                      onChange={handleChange}
                      className={`w-full bg-gray-900 border rounded-lg py-3 px-4 focus:outline-none focus:border-blue-500 ${
                        errors.fullName ? 'border-red-500' : 'border-gray-700'
                      }`}
                      placeholder="Enter your full name"
                    />
                    {errors.fullName && (
                      <p className="text-red-500 text-xs mt-1">{errors.fullName}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Age</label>
                    <input
                      type="number"
                      name="age"
                      value={formData.age}
                      onChange={handleChange}
                      className={`w-full bg-gray-900 border rounded-lg py-3 px-4 focus:outline-none focus:border-blue-500 ${
                        errors.age ? 'border-red-500' : 'border-gray-700'
                      }`}
                      placeholder="Enter your age"
                      min="0"
                      max="120"
                    />
                    {errors.age && (
                      <p className="text-red-500 text-xs mt-1">{errors.age}</p>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex justify-end">
                <Button 
                  type="button" 
                  onClick={nextStep}
                >
                  Next Step →
                </Button>
              </div>
            </div>
          )}

          {/* Step 2: Claim Details */}
          {currentStep === 2 && (
            <div className="space-y-6">
              <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <FiActivity className="text-blue-500" />
                  Claim Details
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium mb-2">Admission Date</label>
                    <div className="relative">
                      <FiCalendar className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                      <input
                        type="date"
                        name="admissionDate"
                        value={formData.admissionDate}
                        onChange={handleChange}
                        className={`w-full bg-gray-900 border rounded-lg py-3 pl-10 pr-4 focus:outline-none focus:border-blue-500 ${
                          errors.admissionDate ? 'border-red-500' : 'border-gray-700'
                        }`}
                      />
                    </div>
                    {errors.admissionDate && (
                      <p className="text-red-500 text-xs mt-1">{errors.admissionDate}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Discharge Date</label>
                    <div className="relative">
                      <FiCalendar className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                      <input
                        type="date"
                        name="dischargeDate"
                        value={formData.dischargeDate}
                        onChange={handleChange}
                        className={`w-full bg-gray-900 border rounded-lg py-3 pl-10 pr-4 focus:outline-none focus:border-blue-500 ${
                          errors.dischargeDate ? 'border-red-500' : 'border-gray-700'
                        }`}
                      />
                    </div>
                    {errors.dischargeDate && (
                      <p className="text-red-500 text-xs mt-1">{errors.dischargeDate}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Disease/Condition</label>
                    <select
                      name="disease"
                      value={formData.disease}
                      onChange={handleChange}
                      className={`w-full bg-gray-900 border rounded-lg py-3 px-4 focus:outline-none focus:border-blue-500 ${
                        errors.disease ? 'border-red-500' : 'border-gray-700'
                      }`}
                    >
                      {diseases.map(d => (
                        <option key={d} value={d}>{d}</option>
                      ))}
                    </select>
                    {errors.disease && (
                      <p className="text-red-500 text-xs mt-1">{errors.disease}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">Claim Amount ($)</label>
                    <div className="relative">
                      <FiDollarSign className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                      <input
                        type="number"
                        name="amount"
                        value={formData.amount}
                        onChange={handleChange}
                        className={`w-full bg-gray-900 border rounded-lg py-3 pl-10 pr-4 focus:outline-none focus:border-blue-500 ${
                          errors.amount ? 'border-red-500' : 'border-gray-700'
                        }`}
                        placeholder="Enter amount"
                        min="0"
                        step="0.01"
                      />
                    </div>
                    {errors.amount && (
                      <p className="text-red-500 text-xs mt-1">{errors.amount}</p>
                    )}
                  </div>
                </div>

                {/* Stay Duration Display */}
                {getStayDuration() && (
                  <div className="mt-4 pt-4 border-t border-gray-700">
                    <p className="text-sm text-gray-400">
                      Stay Duration: <span className="text-white font-medium">{getStayDuration()}</span>
                    </p>
                  </div>
                )}
              </div>

              <div className="flex justify-between">
                <Button type="button" variant="secondary" onClick={prevStep}>
                  ← Previous
                </Button>
                <Button 
                  type="button" 
                  onClick={nextStep}
                  
                >
                  Next Step →
                </Button>
              </div>
            </div>
          )}

          {/* Step 3: Document Upload & ML Review */}
          {currentStep === 3 && (
            <div className="space-y-6">
              
              {/* Document Upload */}
              <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
                  <FiFileText className="text-blue-500" />
                  Upload Supporting Documents
                </h2>
                
                <FileUploader onDrop={handleFileDrop} />

                {/* File List */}
                {files.length > 0 && (
                  <div className="mt-6">
                    <p className="text-sm font-medium mb-3">Uploaded Files ({files.length}):</p>
                    <div className="space-y-2">
                      {files.map((file, index) => (
                        <div key={index} className="flex items-center justify-between bg-gray-900 p-3 rounded-lg">
                          <div className="flex items-center gap-3">
                            <FiFileText className="text-blue-500" />
                            <div>
                              <span className="text-sm">{file.name}</span>
                              <span className="text-xs text-gray-400 ml-2">
                                ({(file.size / 1024).toFixed(2)} KB)
                              </span>
                            </div>
                          </div>
                          <button
                            type="button"
                            onClick={() => removeFile(index)}
                            className="text-red-500 hover:text-red-400 text-sm"
                          >
                            Remove
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <p className="text-xs text-gray-400 mt-4">
                  Supported formats: PDF, JPG, PNG, TXT (Max size: 10MB each)
                </p>
              </div>

              {/* Error Message */}
              {submitError && (
                <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 flex items-center gap-3">
                  <FiAlertCircle className="text-red-500 flex-shrink-0" />
                  <p className="text-red-500 text-sm">{submitError}</p>
                </div>
              )}

              {/* Submit Buttons */}
              <div className="flex justify-between">
                <Button type="button" variant="secondary" onClick={prevStep}>
                  ← Previous
                </Button>
                <Button 
                  type="submit" 
                  disabled={isSubmitting}
                >
                  Submit Claim
                </Button>
              </div>
              </div>
          )}
        </form>
      </main>
    </div>
  );
}