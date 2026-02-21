import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import Button from '../../components/Button';
import StatusBadge from '../../components/StatusBadge';
import { 
  FiSearch, 
  FiFilter, 
  FiDownload, 
  FiEye, 
  FiArrowLeft,
  FiCalendar,
  FiDollarSign,
  FiUser,
  FiActivity,
  FiClock,
  FiAlertCircle,
  FiCheckCircle,
  FiRefreshCw,
  FiFileText,
  FiPrinter,
  FiTrash2
} from 'react-icons/fi';
import { CLAIM_STATUS } from '../../utils/constants';
import { getHospitalClaims, deleteClaim } from '../../services/claims';
import { formatClaimFromApi } from '../../utils/apiHelpers';

export default function HospitalClaimsList() {
  const location = useLocation();
  const successMessage = location.state?.message;
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedClaims, setSelectedClaims] = useState([]);
  const [selectAll, setSelectAll] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [claimToDelete, setClaimToDelete] = useState(null);
  const [deleteInProgress, setDeleteInProgress] = useState(false);
  const [claims, setClaims] = useState([]);

  // Filter states
  const [filters, setFilters] = useState({
    search: '',
    status: 'all',
    department: 'all',
    dateRange: 'all',
    riskLevel: 'all',
    insuranceProvider: 'all',
    startDate: '',
    endDate: ''
  });

  // Sorting state
  const [sortConfig, setSortConfig] = useState({
    key: 'date',
    direction: 'desc'
  });

  // Department options
  const departments = [
    'all',
    'Cardiology',
    'Orthopedics',
    'Emergency',
    'Neurology',
    'Oncology',
    'Pediatrics',
    'General Medicine',
    'Surgery',
    'ICU'
  ];

  // Insurance providers
  const insuranceProviders = [
    'all',
    'Blue Cross',
    'Aetna',
    'Cigna',
    'UnitedHealth',
    'Medicare',
    'Medicaid'
  ];

  // Load claims
  useEffect(() => {
    fetchClaims();
  }, []);

  const fetchClaims = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await getHospitalClaims();
      const formattedClaims = response.claims.map(formatClaimFromApi);
      setClaims(formattedClaims);
    } catch (err) {
      console.error('Failed to fetch claims:', err);
      setError('Failed to load claims. Please refresh.');
    } finally {
      setLoading(false);
    }
  };

  // Filter claims based on all criteria
  const filteredClaims = claims.filter(claim => {
    const matchesSearch = filters.search === '' || 
      claim.id.toLowerCase().includes(filters.search.toLowerCase()) ||
      claim.patientName?.toLowerCase().includes(filters.search.toLowerCase()) ||
      claim.patientId?.toLowerCase().includes(filters.search.toLowerCase()) ||
      claim.doctor?.toLowerCase().includes(filters.search.toLowerCase());

    const matchesStatus = filters.status === 'all' || claim.status === filters.status;
    const matchesDepartment = filters.department === 'all' || claim.department === filters.department;

    const matchesRisk = filters.riskLevel === 'all' || 
      (filters.riskLevel === 'low' && claim.risk <= 30) ||
      (filters.riskLevel === 'medium' && claim.risk > 30 && claim.risk <= 60) ||
      (filters.riskLevel === 'high' && claim.risk > 60 && claim.risk <= 80) ||
      (filters.riskLevel === 'critical' && claim.risk > 80);

    const matchesInsurance = filters.insuranceProvider === 'all' || 
      claim.insuranceProvider === filters.insuranceProvider;

    let matchesDate = true;
    const claimDate = new Date(claim.date);
    const today = new Date();
    
    if (filters.dateRange === 'today') {
      matchesDate = claimDate.toDateString() === today.toDateString();
    } else if (filters.dateRange === 'week') {
      const weekAgo = new Date(today.setDate(today.getDate() - 7));
      matchesDate = claimDate >= weekAgo;
    } else if (filters.dateRange === 'month') {
      const monthAgo = new Date(today.setMonth(today.getMonth() - 1));
      matchesDate = claimDate >= monthAgo;
    } else if (filters.dateRange === 'custom') {
      if (filters.startDate && filters.endDate) {
        matchesDate = claimDate >= new Date(filters.startDate) && 
                     claimDate <= new Date(filters.endDate);
      }
    }

    return matchesSearch && matchesStatus && matchesDepartment && 
           matchesRisk && matchesInsurance && matchesDate;
  });

  // Sort claims
  const sortedClaims = [...filteredClaims].sort((a, b) => {
    let aValue = a[sortConfig.key];
    let bValue = b[sortConfig.key];

    if (sortConfig.key === 'amount' || sortConfig.key === 'risk') {
      aValue = Number(aValue?.replace('$', '') || 0);
      bValue = Number(bValue?.replace('$', '') || 0);
    }

    if (aValue < bValue) {
      return sortConfig.direction === 'asc' ? -1 : 1;
    }
    if (aValue > bValue) {
      return sortConfig.direction === 'asc' ? 1 : -1;
    }
    return 0;
  });

  // Calculate summary stats
  const stats = {
    total: filteredClaims.length,
    totalAmount: filteredClaims.reduce((sum, claim) => {
      const amount = parseFloat(claim.amount?.replace('$', '') || 0);
      return sum + amount;
    }, 0),
    pending: filteredClaims.filter(c => 
      [CLAIM_STATUS.SUBMITTED, CLAIM_STATUS.AI_PROCESSING, CLAIM_STATUS.MANUAL_REVIEW].includes(c.status)
    ).length,
    flagged: filteredClaims.filter(c => c.status === CLAIM_STATUS.FLAGGED).length,
    fraud: filteredClaims.filter(c => c.status === CLAIM_STATUS.FRAUD).length,
    approved: filteredClaims.filter(c => c.status === CLAIM_STATUS.APPROVED).length
  };

  const handleSort = (key) => {
    setSortConfig({
      key,
      direction: sortConfig.key === key && sortConfig.direction === 'asc' ? 'desc' : 'asc'
    });
  };

  const handleSelectClaim = (claimId) => {
    setSelectedClaims(prev => {
      if (prev.includes(claimId)) {
        return prev.filter(id => id !== claimId);
      } else {
        return [...prev, claimId];
      }
    });
  };

  const handleSelectAllChange = () => {
    const newSelectAll = !selectAll;
    setSelectAll(newSelectAll);
    if (newSelectAll) {
      setSelectedClaims(filteredClaims.map(claim => claim.id));
    } else {
      setSelectedClaims([]);
    }
  };

  const handleDeleteClick = (claim) => {
    setClaimToDelete(claim);
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!claimToDelete) return;
    
    setDeleteInProgress(true);
    
    try {
      await deleteClaim(claimToDelete.id);
      
      // Update local state
      const updatedClaims = claims.filter(c => c.id !== claimToDelete.id);
      setClaims(updatedClaims);
      
      // Clear selection if needed
      if (selectedClaims.includes(claimToDelete.id)) {
        setSelectedClaims(prev => prev.filter(id => id !== claimToDelete.id));
      }
      
      setShowDeleteModal(false);
      setClaimToDelete(null);
      
    } catch (err) {
      console.error('Delete failed:', err);
      setError('Failed to delete claim. Please try again.');
    } finally {
      setDeleteInProgress(false);
    }
  };

  const cancelDelete = () => {
    setShowDeleteModal(false);
    setClaimToDelete(null);
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      status: 'all',
      department: 'all',
      dateRange: 'all',
      riskLevel: 'all',
      insuranceProvider: 'all',
      startDate: '',
      endDate: ''
    });
  };

  const getSortIcon = (key) => {
    if (sortConfig.key !== key) return null;
    return sortConfig.direction === 'asc' ? '↑' : '↓';
  };

  const getRiskColor = (risk) => {
    if (risk > 80) return 'text-danger';
    if (risk > 60) return 'text-orange-500';
    if (risk > 40) return 'text-warning';
    if (risk > 20) return 'text-info';
    return 'text-success';
  };

  const exportToCSV = () => {
    const headers = ['Claim ID', 'Patient', 'Date', 'Amount', 'Status', 'Risk', 'Department', 'Doctor', 'Insurance'];
    const csvData = filteredClaims.map(claim => [
      claim.id,
      claim.patientName,
      claim.date,
      claim.amount,
      claim.status,
      `${claim.risk}%`,
      claim.department,
      claim.doctor,
      claim.insuranceProvider
    ]);
    
    const csv = [headers, ...csvData].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `hospital-claims-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  return (
    <div className="min-h-screen bg-background text-white">
      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-surface rounded-xl border border-gray-800 max-w-md w-full p-6">
            <div className="flex items-center gap-3 text-danger mb-4">
              <FiAlertCircle className="text-3xl" />
              <h2 className="text-xl font-bold">Delete Claim</h2>
            </div>
            
            <p className="text-textSecondary mb-2">
              Are you sure you want to delete claim <span className="font-mono text-primary">{claimToDelete?.id}</span>?
            </p>
            <p className="text-sm text-textSecondary mb-4">
              Patient: <span className="text-white">{claimToDelete?.patientName}</span>
            </p>
            <p className="text-sm text-textSecondary mb-6">
              This action cannot be undone.
            </p>

            <div className="flex gap-3 justify-end">
              <Button 
                variant="secondary" 
                onClick={cancelDelete}
                disabled={deleteInProgress}
              >
                Cancel
              </Button>
              <Button 
                variant="danger"
                onClick={confirmDelete}
                disabled={deleteInProgress}
              >
                {deleteInProgress ? 'Deleting...' : 'Delete Permanently'}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <header className="bg-surface/50 backdrop-blur-sm border-b border-gray-800 sticky top-0 z-40">
        <div className="px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link 
              to="/hospital/dashboard" 
              className="p-2 hover:bg-surface rounded-lg transition-colors"
            >
              <FiArrowLeft className="text-xl" />
            </Link>
            <h1 className="text-xl font-bold">Claims Management</h1>
            <span className="text-sm bg-primary/20 text-primary px-3 py-1 rounded-full">
              {stats.total} Claims
            </span>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-3">
            <Button 
              variant="secondary" 
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2"
            >
              <FiFilter />
              Filters
              {(filters.search || filters.status !== 'all' || filters.department !== 'all') && (
                <span className="w-2 h-2 bg-primary rounded-full"></span>
              )}
            </Button>
            
            <Button 
              variant="secondary" 
              size="sm"
              onClick={exportToCSV}
              className="flex items-center gap-2"
              disabled={filteredClaims.length === 0}
            >
              <FiDownload />
              Export
            </Button>

            <Button 
              variant="secondary" 
              size="sm"
              onClick={fetchClaims}
            >
              <FiRefreshCw />
            </Button>
          </div>
        </div>
      </header>

      {/* Success Message */}
      {successMessage && (
        <div className="px-6 pt-6">
          <div className="bg-success/10 border border-success/30 text-success px-4 py-3 rounded-lg flex items-center gap-3">
            <FiCheckCircle />
            {successMessage}
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="px-6 pt-6">
          <div className="bg-danger/10 border border-danger/30 text-danger px-4 py-3 rounded-lg">
            {error}
          </div>
        </div>
      )}

      {/* Filters Panel */}
      {showFilters && (
        <div className="px-6 pt-6">
          <div className="bg-surface rounded-xl border border-gray-800 p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="font-bold flex items-center gap-2">
                <FiFilter className="text-primary" />
                Advanced Filters
              </h2>
              <button 
                onClick={clearFilters}
                className="text-sm text-primary hover:underline"
              >
                Clear all filters
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Search */}
              <div>
                <label className="block text-sm text-textSecondary mb-2">Search</label>
                <div className="relative">
                  <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-textSecondary" />
                  <input
                    type="text"
                    placeholder="ID, patient, doctor..."
                    value={filters.search}
                    onChange={(e) => setFilters({...filters, search: e.target.value})}
                    className="w-full bg-background border border-gray-800 rounded-lg py-2 pl-10 pr-4 focus:outline-none focus:border-primary"
                  />
                </div>
              </div>

              {/* Status Filter */}
              <div>
                <label className="block text-sm text-textSecondary mb-2">Status</label>
                <select
                  value={filters.status}
                  onChange={(e) => setFilters({...filters, status: e.target.value})}
                  className="w-full bg-background border border-gray-800 rounded-lg py-2 px-3 focus:outline-none focus:border-primary"
                >
                  <option value="all">All Statuses</option>
                  {Object.values(CLAIM_STATUS).map(status => (
                    <option key={status} value={status}>{status}</option>
                  ))}
                </select>
              </div>

              {/* Department Filter */}
              <div>
                <label className="block text-sm text-textSecondary mb-2">Department</label>
                <select
                  value={filters.department}
                  onChange={(e) => setFilters({...filters, department: e.target.value})}
                  className="w-full bg-background border border-gray-800 rounded-lg py-2 px-3 focus:outline-none focus:border-primary"
                >
                  {departments.map(dept => (
                    <option key={dept} value={dept}>
                      {dept === 'all' ? 'All Departments' : dept}
                    </option>
                  ))}
                </select>
              </div>

              {/* Insurance Provider */}
              <div>
                <label className="block text-sm text-textSecondary mb-2">Insurance</label>
                <select
                  value={filters.insuranceProvider}
                  onChange={(e) => setFilters({...filters, insuranceProvider: e.target.value})}
                  className="w-full bg-background border border-gray-800 rounded-lg py-2 px-3 focus:outline-none focus:border-primary"
                >
                  {insuranceProviders.map(provider => (
                    <option key={provider} value={provider}>
                      {provider === 'all' ? 'All Providers' : provider}
                    </option>
                  ))}
                </select>
              </div>

              {/* Date Range */}
              <div>
                <label className="block text-sm text-textSecondary mb-2">Date Range</label>
                <select
                  value={filters.dateRange}
                  onChange={(e) => setFilters({...filters, dateRange: e.target.value})}
                  className="w-full bg-background border border-gray-800 rounded-lg py-2 px-3 focus:outline-none focus:border-primary"
                >
                  <option value="all">All Time</option>
                  <option value="today">Today</option>
                  <option value="week">Last 7 Days</option>
                  <option value="month">Last 30 Days</option>
                  <option value="custom">Custom Range</option>
                </select>
              </div>

              {/* Custom Date Range */}
              {filters.dateRange === 'custom' && (
                <>
                  <div>
                    <label className="block text-sm text-textSecondary mb-2">Start Date</label>
                    <input
                      type="date"
                      value={filters.startDate}
                      onChange={(e) => setFilters({...filters, startDate: e.target.value})}
                      className="w-full bg-background border border-gray-800 rounded-lg py-2 px-3 focus:outline-none focus:border-primary"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-textSecondary mb-2">End Date</label>
                    <input
                      type="date"
                      value={filters.endDate}
                      onChange={(e) => setFilters({...filters, endDate: e.target.value})}
                      className="w-full bg-background border border-gray-800 rounded-lg py-2 px-3 focus:outline-none focus:border-primary"
                    />
                  </div>
                </>
              )}

              {/* Risk Level */}
              <div>
                <label className="block text-sm text-textSecondary mb-2">Risk Level</label>
                <select
                  value={filters.riskLevel}
                  onChange={(e) => setFilters({...filters, riskLevel: e.target.value})}
                  className="w-full bg-background border border-gray-800 rounded-lg py-2 px-3 focus:outline-none focus:border-primary"
                >
                  <option value="all">All Risk Levels</option>
                  <option value="low">Low (0-30)</option>
                  <option value="medium">Medium (31-60)</option>
                  <option value="high">High (61-80)</option>
                  <option value="critical">Critical (81-100)</option>
                </select>
              </div>
            </div>

            {/* Active Filters Display */}
            <div className="mt-4 flex flex-wrap gap-2">
              {filters.search && (
                <span className="bg-primary/20 text-primary px-3 py-1 rounded-full text-sm flex items-center gap-1">
                  Search: {filters.search}
                  <button onClick={() => setFilters({...filters, search: ''})}>×</button>
                </span>
              )}
              {filters.status !== 'all' && (
                <span className="bg-primary/20 text-primary px-3 py-1 rounded-full text-sm flex items-center gap-1">
                  Status: {filters.status}
                  <button onClick={() => setFilters({...filters, status: 'all'})}>×</button>
                </span>
              )}
              {filters.department !== 'all' && (
                <span className="bg-primary/20 text-primary px-3 py-1 rounded-full text-sm flex items-center gap-1">
                  Dept: {filters.department}
                  <button onClick={() => setFilters({...filters, department: 'all'})}>×</button>
                </span>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Summary Stats */}
      <div className="px-6 pt-6">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-surface/50 rounded-lg border border-gray-800 p-4">
            <p className="text-textSecondary text-sm">Total Claims</p>
            <p className="text-2xl font-bold">{stats.total}</p>
          </div>
          <div className="bg-surface/50 rounded-lg border border-gray-800 p-4">
            <p className="text-textSecondary text-sm">Total Amount</p>
            <p className="text-2xl font-bold text-success">${stats.totalAmount.toLocaleString()}</p>
          </div>
          <div className="bg-surface/50 rounded-lg border border-gray-800 p-4">
            <p className="text-textSecondary text-sm">Pending</p>
            <p className="text-2xl font-bold text-warning">{stats.pending}</p>
          </div>
          <div className="bg-surface/50 rounded-lg border border-gray-800 p-4">
            <p className="text-textSecondary text-sm">Flagged</p>
            <p className="text-2xl font-bold text-orange-500">{stats.flagged}</p>
          </div>
          <div className="bg-surface/50 rounded-lg border border-gray-800 p-4">
            <p className="text-textSecondary text-sm">Approved</p>
            <p className="text-2xl font-bold text-success">{stats.approved}</p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="p-6">
        {loading ? (
          <div className="bg-surface rounded-xl border border-gray-800 p-12 text-center">
            <div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-textSecondary">Loading claims...</p>
          </div>
        ) : (
          <div className="bg-surface rounded-xl border border-gray-800 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-background/50">
                  <tr className="text-left text-textSecondary text-sm">
                    <th className="px-6 py-4 w-10">
                      <input
                        type="checkbox"
                        checked={selectAll}
                        onChange={handleSelectAllChange}
                        className="rounded border-gray-800 bg-surface text-primary focus:ring-primary"
                      />
                    </th>
                    <th className="px-6 py-4 cursor-pointer hover:text-white" onClick={() => handleSort('id')}>
                      Claim ID {getSortIcon('id')}
                    </th>
                    <th className="px-6 py-4 cursor-pointer hover:text-white" onClick={() => handleSort('patientName')}>
                      Patient {getSortIcon('patientName')}
                    </th>
                    <th className="px-6 py-4 cursor-pointer hover:text-white" onClick={() => handleSort('date')}>
                      Date {getSortIcon('date')}
                    </th>
                    <th className="px-6 py-4 cursor-pointer hover:text-white" onClick={() => handleSort('amount')}>
                      Amount {getSortIcon('amount')}
                    </th>
                    <th className="px-6 py-4">Status</th>
                    <th className="px-6 py-4 cursor-pointer hover:text-white" onClick={() => handleSort('risk')}>
                      Risk {getSortIcon('risk')}
                    </th>
                    <th className="px-6 py-4">Department</th>
                    <th className="px-6 py-4">Doctor</th>
                    <th className="px-6 py-4">Insurance</th>
                    <th className="px-6 py-4">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {sortedClaims.map((claim) => (
                    <tr 
                      key={claim.id} 
                      className={`hover:bg-surface/80 transition-colors ${
                        selectedClaims.includes(claim.id) ? 'bg-primary/5' : ''
                      }`}
                    >
                      <td className="px-6 py-4">
                        <input
                          type="checkbox"
                          checked={selectedClaims.includes(claim.id)}
                          onChange={() => handleSelectClaim(claim.id)}
                          className="rounded border-gray-800 bg-surface text-primary focus:ring-primary"
                        />
                      </td>
                      <td className="px-6 py-4 font-mono text-sm">{claim.id}</td>
                      <td className="px-6 py-4">
                        <div>
                          <div className="font-medium">{claim.patientName}</div>
                          <div className="text-xs text-textSecondary">
                            {claim.patientId} • {claim.age}y • {claim.gender}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div>
                          <div>{claim.date}</div>
                          <div className="text-xs text-textSecondary">
                            {claim.submittedAt ? new Date(claim.submittedAt).toLocaleTimeString() : ''}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 font-medium">{claim.amount}</td>
                      <td className="px-6 py-4">
                        <StatusBadge status={claim.status} />
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <div className="w-16 bg-background rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full ${
                                claim.risk > 80 ? 'bg-danger' :
                                claim.risk > 60 ? 'bg-orange-500' :
                                claim.risk > 40 ? 'bg-warning' :
                                claim.risk > 20 ? 'bg-info' : 'bg-success'
                              }`}
                              style={{ width: `${claim.risk}%` }}
                            ></div>
                          </div>
                          <span className={`text-sm font-mono ${getRiskColor(claim.risk)}`}>
                            {claim.risk}%
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">{claim.department}</td>
                      <td className="px-6 py-4">{claim.doctor}</td>
                      <td className="px-6 py-4">
                        <div>
                          <div>{claim.insuranceProvider}</div>
                          <div className="text-xs text-textSecondary">{claim.policyNumber}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <Link 
                            to={`/hospital/claims/${claim.id}`}
                            className="p-2 hover:bg-primary/20 rounded-lg transition-colors"
                            title="View Details"
                          >
                            <FiEye className="text-primary" />
                          </Link>
                          <button 
                            onClick={() => handleDeleteClick(claim)}
                            className="p-2 hover:bg-danger/20 rounded-lg transition-colors"
                            title="Delete Claim"
                          >
                            <FiTrash2 className="text-danger" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Empty State */}
            {filteredClaims.length === 0 && !loading && (
              <div className="p-12 text-center">
                <FiFileText className="text-4xl text-textSecondary mx-auto mb-4" />
                <h3 className="text-lg font-bold mb-2">No claims found</h3>
                <p className="text-textSecondary mb-4">Try adjusting your filters</p>
                <Button onClick={clearFilters}>Clear Filters</Button>
              </div>
            )}

            {/* Pagination */}
            {filteredClaims.length > 0 && (
              <div className="px-6 py-4 border-t border-gray-800 flex items-center justify-between">
                <p className="text-sm text-textSecondary">
                  Showing {filteredClaims.length} of {claims.length} claims
                </p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}