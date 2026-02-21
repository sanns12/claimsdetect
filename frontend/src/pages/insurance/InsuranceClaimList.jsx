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
  FiXCircle,
  FiRefreshCw,
  FiFileText,
  FiPrinter,
  FiBarChart2,
  FiChevronDown,
  FiShield,
  FiFlag,
  FiTrendingUp
} from 'react-icons/fi';
import { CLAIM_STATUS } from '../../utils/constants';

export default function InsuranceClaimsList() {
  const location = useLocation();
  const successMessage = location.state?.message;
  const [loading, setLoading] = useState(true);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedClaims, setSelectedClaims] = useState([]);
  const [selectAll, setSelectAll] = useState(false);
  const [viewMode, setViewMode] = useState('all'); // 'all', 'flagged', 'fraud', 'pending'

  // Filter states
  const [filters, setFilters] = useState({
    search: '',
    status: 'all',
    riskLevel: 'all',
    company: 'all',
    dateRange: 'all',
    amountRange: 'all',
    startDate: '',
    endDate: '',
    minAmount: '',
    maxAmount: ''
  });

  // Sorting state
  const [sortConfig, setSortConfig] = useState({
    key: 'date',
    direction: 'desc'
  });

  // claims will be loaded from API
  const [claims, setClaims] = useState([]);

  // Companies list for filter
  const companies = [
    'all',
    'City General Hospital',
    'MediCare Plus Clinic',
    'HealthFirst Medical',
    'QuickCare Center',
    'Premier Health Group'
  ];

  // Load claims on mount
useEffect(() => {
  const fetchClaims = async () => {
    try {
      setLoading(true);
      const response = await getClaims();
      
      console.log('📥 Insurance claims response:', response);
      
      // The response should be { claims: [...] }
      const claimsArray = response?.claims || [];
      
      if (claimsArray.length === 0) {
        console.log('No claims found');
        setClaims([]);
        return;
      }
      
      // Map API claims to UI shape
      const mapped = claimsArray.map(c => ({
        id: c.id || c.claim_id || `CLM${c.id}`,
        patientName: c.patient_name || c.patientName || 'Unknown',
        hospital: c.hospital_name || c.hospital || '',
        date: c.created_at ? c.created_at.split('T')[0] : (c.date || ''),
        amount: typeof c.amount === 'number' ? c.amount : parseFloat(c.claim_amount) || 0,
        status: c.status || CLAIM_STATUS.SUBMITTED,
        risk: c.risk_score || c.risk || 0,
        fraudScore: c.fraud_probability || c.fraud_score || 0,
        flags: c.flags || [],
        department: c.department || null,
        insuranceProvider: c.insurance_provider || null,
        priority: c.priority || 'normal'
      }));
      
      console.log(`✅ Mapped ${mapped.length} claims for display`);
      setClaims(mapped);
    } catch (err) {
      console.error('❌ Failed to load claims:', err);
      setClaims([]);
    } finally {
      setLoading(false);
    }
  };
  
  fetchClaims();
}, []);

  // Filter claims based on view mode and filters
  const filteredClaims = claims.filter(claim => {
    // View mode filter
    if (viewMode === 'flagged' && claim.status !== CLAIM_STATUS.FLAGGED) return false;
    if (viewMode === 'fraud' && claim.status !== CLAIM_STATUS.FRAUD) return false;
    if (viewMode === 'pending' && ![CLAIM_STATUS.SUBMITTED, CLAIM_STATUS.AI_PROCESSING, CLAIM_STATUS.MANUAL_REVIEW].includes(claim.status)) return false;

    // Search filter
    const matchesSearch = filters.search === '' || 
      claim.id.toLowerCase().includes(filters.search.toLowerCase()) ||
      claim.patientName.toLowerCase().includes(filters.search.toLowerCase()) ||
      claim.hospital.toLowerCase().includes(filters.search.toLowerCase());

    // Status filter
    const matchesStatus = filters.status === 'all' || claim.status === filters.status;

    // Risk level filter
    const matchesRisk = filters.riskLevel === 'all' || 
      (filters.riskLevel === 'low' && claim.risk <= 30) ||
      (filters.riskLevel === 'medium' && claim.risk > 30 && claim.risk <= 60) ||
      (filters.riskLevel === 'high' && claim.risk > 60 && claim.risk <= 80) ||
      (filters.riskLevel === 'critical' && claim.risk > 80);

    // Company filter
    const matchesCompany = filters.company === 'all' || claim.hospital === filters.company;

    // Amount range filter
    let matchesAmount = true;
    if (filters.amountRange === 'under5k') matchesAmount = claim.amount < 5000;
    else if (filters.amountRange === '5k-10k') matchesAmount = claim.amount >= 5000 && claim.amount <= 10000;
    else if (filters.amountRange === '10k-25k') matchesAmount = claim.amount > 10000 && claim.amount <= 25000;
    else if (filters.amountRange === 'over25k') matchesAmount = claim.amount > 25000;

    // Date range filter
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
    }

    return matchesSearch && matchesStatus && matchesRisk && 
           matchesCompany && matchesAmount && matchesDate;
  });

  // Sort claims
  const sortedClaims = [...filteredClaims].sort((a, b) => {
    let aValue = a[sortConfig.key];
    let bValue = b[sortConfig.key];

    if (sortConfig.key === 'amount' || sortConfig.key === 'risk' || sortConfig.key === 'fraudScore') {
      aValue = Number(aValue);
      bValue = Number(bValue);
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
    totalAmount: filteredClaims.reduce((sum, claim) => sum + claim.amount, 0),
    fraudCount: filteredClaims.filter(c => c.status === CLAIM_STATUS.FRAUD).length,
    flaggedCount: filteredClaims.filter(c => c.status === CLAIM_STATUS.FLAGGED).length,
    pendingCount: filteredClaims.filter(c => 
      [CLAIM_STATUS.SUBMITTED, CLAIM_STATUS.AI_PROCESSING, CLAIM_STATUS.MANUAL_REVIEW].includes(c.status)
    ).length,
    avgRisk: Math.round(filteredClaims.reduce((sum, claim) => sum + claim.risk, 0) / filteredClaims.length) || 0
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

  const handleBulkAction = (action) => {
    console.log(`Bulk ${action} for claims:`, selectedClaims);
  };

  const clearFilters = () => {
    setFilters({
      search: '',
      status: 'all',
      riskLevel: 'all',
      company: 'all',
      dateRange: 'all',
      amountRange: 'all',
      startDate: '',
      endDate: '',
      minAmount: '',
      maxAmount: ''
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
    return 'text-success';
  };

  const exportToCSV = () => {
    const headers = ['Claim ID', 'Patient', 'Hospital', 'Date', 'Amount', 'Status', 'Risk', 'Fraud Score', 'Flags'];
    const csvData = filteredClaims.map(claim => [
      claim.id,
      claim.patientName,
      claim.hospital,
      claim.date,
      claim.amount,
      claim.status,
      `${claim.risk}%`,
      claim.fraudScore,
      claim.flags.join('; ')
    ]);
    
    const csv = [headers, ...csvData].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `insurance-claims-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  return (
    <div className="min-h-screen bg-background text-white">
      {/* Header */}
      <header className="bg-surface/50 backdrop-blur-sm border-b border-gray-800 sticky top-0 z-50">
        <div className="px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link 
              to="/insurance/dashboard" 
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
            </Button>
            
            <Button 
              variant="secondary" 
              size="sm"
              onClick={exportToCSV}
              className="flex items-center gap-2"
            >
              <FiDownload />
              Export
            </Button>

            <Button 
              variant="secondary" 
              size="sm"
              onClick={() => window.location.reload()}
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

      {/* View Mode Tabs */}
      <div className="px-6 pt-6">
        <div className="flex gap-2 border-b border-gray-800">
          <button
            onClick={() => setViewMode('all')}
            className={`px-4 py-2 font-medium transition-colors relative ${
              viewMode === 'all' ? 'text-primary' : 'text-textSecondary hover:text-white'
            }`}
          >
            All Claims
            {viewMode === 'all' && <div className="absolute bottom-0 left-0 w-full h-0.5 bg-primary"></div>}
          </button>
          <button
            onClick={() => setViewMode('pending')}
            className={`px-4 py-2 font-medium transition-colors relative ${
              viewMode === 'pending' ? 'text-warning' : 'text-textSecondary hover:text-white'
            }`}
          >
            Pending Review
            {viewMode === 'pending' && <div className="absolute bottom-0 left-0 w-full h-0.5 bg-warning"></div>}
          </button>
          <button
            onClick={() => setViewMode('flagged')}
            className={`px-4 py-2 font-medium transition-colors relative ${
              viewMode === 'flagged' ? 'text-orange-500' : 'text-textSecondary hover:text-white'
            }`}
          >
            Flagged
            {viewMode === 'flagged' && <div className="absolute bottom-0 left-0 w-full h-0.5 bg-orange-500"></div>}
          </button>
          <button
            onClick={() => setViewMode('fraud')}
            className={`px-4 py-2 font-medium transition-colors relative ${
              viewMode === 'fraud' ? 'text-danger' : 'text-textSecondary hover:text-white'
            }`}
          >
            Fraud Cases
            {viewMode === 'fraud' && <div className="absolute bottom-0 left-0 w-full h-0.5 bg-danger"></div>}
          </button>
        </div>
      </div>

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
                    placeholder="ID, patient, hospital..."
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

              {/* Risk Level */}
              <div>
                <label className="block text-sm text-textSecondary mb-2">Risk Level</label>
                <select
                  value={filters.riskLevel}
                  onChange={(e) => setFilters({...filters, riskLevel: e.target.value})}
                  className="w-full bg-background border border-gray-800 rounded-lg py-2 px-3 focus:outline-none focus:border-primary"
                >
                  <option value="all">All Risks</option>
                  <option value="low">Low (0-30)</option>
                  <option value="medium">Medium (31-60)</option>
                  <option value="high">High (61-80)</option>
                  <option value="critical">Critical (81-100)</option>
                </select>
              </div>

              {/* Company/Hospital */}
              <div>
                <label className="block text-sm text-textSecondary mb-2">Hospital</label>
                <select
                  value={filters.company}
                  onChange={(e) => setFilters({...filters, company: e.target.value})}
                  className="w-full bg-background border border-gray-800 rounded-lg py-2 px-3 focus:outline-none focus:border-primary"
                >
                  {companies.map(company => (
                    <option key={company} value={company}>
                      {company === 'all' ? 'All Hospitals' : company}
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
                </select>
              </div>

              {/* Amount Range */}
              <div>
                <label className="block text-sm text-textSecondary mb-2">Amount Range</label>
                <select
                  value={filters.amountRange}
                  onChange={(e) => setFilters({...filters, amountRange: e.target.value})}
                  className="w-full bg-background border border-gray-800 rounded-lg py-2 px-3 focus:outline-none focus:border-primary"
                >
                  <option value="all">All Amounts</option>
                  <option value="under5k">Under $5,000</option>
                  <option value="5k-10k">$5,000 - $10,000</option>
                  <option value="10k-25k">$10,000 - $25,000</option>
                  <option value="over25k">Over $25,000</option>
                </select>
              </div>
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
            <p className="text-2xl font-bold text-warning">{stats.pendingCount}</p>
          </div>
          <div className="bg-surface/50 rounded-lg border border-gray-800 p-4">
            <p className="text-textSecondary text-sm">Flagged</p>
            <p className="text-2xl font-bold text-orange-500">{stats.flaggedCount}</p>
          </div>
          <div className="bg-surface/50 rounded-lg border border-gray-800 p-4">
            <p className="text-textSecondary text-sm">Fraud</p>
            <p className="text-2xl font-bold text-danger">{stats.fraudCount}</p>
          </div>
        </div>
      </div>

      {/* Bulk Actions Bar */}
      {selectedClaims.length > 0 && (
        <div className="px-6 pt-4">
          <div className="bg-primary/10 border border-primary/30 rounded-lg p-3 flex items-center justify-between">
            <span className="text-sm">
              <span className="font-bold">{selectedClaims.length}</span> claims selected
            </span>
            <div className="flex gap-2">
              <Button size="sm" variant="secondary" onClick={() => handleBulkAction('approve')}>
                Approve
              </Button>
              <Button size="sm" variant="secondary" onClick={() => handleBulkAction('flag')}>
                Flag
              </Button>
              <Button size="sm" variant="secondary" onClick={() => handleBulkAction('fraud')}>
                Mark Fraud
              </Button>
              <Button size="sm" variant="secondary" onClick={() => setSelectedClaims([])}>
                Clear
              </Button>
            </div>
          </div>
        </div>
      )}

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
                    <th className="px-6 py-4">Hospital</th>
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
                    <th className="px-6 py-4">Fraud Score</th>
                    <th className="px-6 py-4">Flags</th>
                    <th className="px-6 py-4">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {sortedClaims.map((claim) => (
                    <tr 
                      key={claim.id} 
                      className={`hover:bg-surface/80 transition-colors ${
                        selectedClaims.includes(claim.id) ? 'bg-primary/5' : ''
                      } ${
                        claim.priority === 'urgent' ? 'border-l-2 border-l-danger' : ''
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
                            {claim.department || '-'}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div>
                          <div>{claim.hospital}</div>
                          <div className="text-xs text-textSecondary">
                            {claim.insuranceProvider || '-'}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div>{claim.date}</div>
                      </td>
                      <td className="px-6 py-4 font-medium">${claim.amount.toLocaleString()}</td>
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
                                claim.risk > 40 ? 'bg-warning' : 'bg-success'
                              }`}
                              style={{ width: `${claim.risk}%` }}
                            ></div>
                          </div>
                          <span className={`text-sm font-mono ${getRiskColor(claim.risk)}`}>
                            {claim.risk}%
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          claim.fraudScore > 0.8 ? 'bg-danger/20 text-danger' :
                          claim.fraudScore > 0.6 ? 'bg-warning/20 text-warning' :
                          'bg-success/20 text-success'
                        }`}>
                          {(claim.fraudScore * 100).toFixed(0)}%
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex flex-wrap gap-1">
                          {claim.flags.map((flag, idx) => (
                            <span key={idx} className="text-xs bg-primary/20 text-primary px-2 py-1 rounded-full">
                              {flag}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <Link 
                          to={`/insurance/claims/${claim.id}`}
                          className="p-2 hover:bg-primary/20 rounded-lg transition-colors inline-block"
                          title="View Details"
                        >
                          <FiEye className="text-primary" />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Empty State */}
            {filteredClaims.length === 0 && (
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
                <div className="flex gap-2">
                  <button className="px-3 py-1 bg-background rounded-lg border border-gray-800 hover:border-primary transition-colors disabled:opacity-50" disabled>
                    Previous
                  </button>
                  <button className="px-3 py-1 bg-primary rounded-lg hover:bg-primary/90 transition-colors">
                    1
                  </button>
                  <button className="px-3 py-1 bg-background rounded-lg border border-gray-800 hover:border-primary transition-colors">
                    2
                  </button>
                  <button className="px-3 py-1 bg-background rounded-lg border border-gray-800 hover:border-primary transition-colors">
                    3
                  </button>
                  <button className="px-3 py-1 bg-background rounded-lg border border-gray-800 hover:border-primary transition-colors">
                    Next
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}