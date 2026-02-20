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
  FiTrash2,
  FiAlertCircle,
  FiCheckCircle
} from 'react-icons/fi';
import { CLAIM_STATUS } from '../../utils/constants';

export default function UserClaimList() {
  const location = useLocation();
  const successMessage = location.state?.message;
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [dateFilter, setDateFilter] = useState('');
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [claimToDelete, setClaimToDelete] = useState(null);
  const [deleteInProgress, setDeleteInProgress] = useState(false);

  const loadClaims = () => {
    const storedClaims = JSON.parse(localStorage.getItem('userClaims') || '[]');
    
    setTimeout(() => {
      if (storedClaims.length === 0) {
        const mockClaims = [
          { 
            id: 'CLM001', 
            date: '2024-03-15', 
            amount: '$5,200', 
            status: CLAIM_STATUS.APPROVED, 
            risk: 23,
            disease: 'Cardiovascular',
            hospital: 'City General Hospital'
          },
          { 
            id: 'CLM002', 
            date: '2024-03-14', 
            amount: '$12,500', 
            status: CLAIM_STATUS.AI_PROCESSING, 
            risk: 67,
            disease: 'Orthopedic',
            hospital: 'St. Mary\'s Medical'
          },
          { 
            id: 'CLM003', 
            date: '2024-03-13', 
            amount: '$3,800', 
            status: CLAIM_STATUS.FLAGGED, 
            risk: 82,
            disease: 'Respiratory',
            hospital: 'Community Health Center'
          },
          { 
            id: 'CLM004', 
            date: '2024-03-12', 
            amount: '$8,900', 
            status: CLAIM_STATUS.SUBMITTED, 
            risk: 45,
            disease: 'Gastrointestinal',
            hospital: 'University Hospital'
          }
        ];
        setClaims(mockClaims);
        localStorage.setItem('userClaims', JSON.stringify(mockClaims));
      } else {
        setClaims(storedClaims);
      }
      setLoading(false);
    }, 500);
  };

  // Load claims from localStorage on component mount
  useEffect(() => {
    loadClaims();
  }, []);

  // Filter claims based on search and filters
  const filteredClaims = claims.filter(claim => {
    const matchesSearch = searchTerm === '' || 
      claim.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (claim.disease && claim.disease.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (claim.hospital && claim.hospital.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesStatus = statusFilter === 'all' || claim.status === statusFilter;
    const matchesDate = !dateFilter || claim.date === dateFilter;
    
    return matchesSearch && matchesStatus && matchesDate;
  });

  const handleDeleteClick = (claim) => {
    setClaimToDelete(claim);
    setShowDeleteModal(true);
  };

  const confirmDelete = () => {
    if (!claimToDelete) return;
    
    setDeleteInProgress(true);
    
    // Simulate API call
    setTimeout(() => {
      // Remove claim from array
      const updatedClaims = claims.filter(c => c.id !== claimToDelete.id);
      
      // Update localStorage
      localStorage.setItem('userClaims', JSON.stringify(updatedClaims));
      
      // Update state
      setClaims(updatedClaims);
      
      // Close modal
      setShowDeleteModal(false);
      setClaimToDelete(null);
      setDeleteInProgress(false);
    }, 1000);
  };

  const cancelDelete = () => {
    setShowDeleteModal(false);
    setClaimToDelete(null);
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
            <p className="text-sm text-textSecondary mb-6">
              This action cannot be undone. All documents associated with this claim will be permanently removed.
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
        <div className="px-6 py-4 flex items-center gap-4">
          <Link 
            to="/user/dashboard" 
            className="p-2 hover:bg-surface rounded-lg transition-colors"
          >
            <FiArrowLeft className="text-xl" />
          </Link>
          <h1 className="text-xl font-bold">My Claims</h1>
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

      {/* Main Content */}
      <main className="p-6">
        {/* Filters Bar */}
        <div className="bg-surface rounded-xl border border-gray-800 p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-textSecondary" />
              <input
                type="text"
                placeholder="Search claims..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-background border border-gray-800 rounded-lg py-2 pl-10 pr-4 focus:outline-none focus:border-primary"
              />
            </div>

            {/* Status Filter */}
            <div className="relative">
              <FiFilter className="absolute left-3 top-1/2 -translate-y-1/2 text-textSecondary" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full bg-background border border-gray-800 rounded-lg py-2 pl-10 pr-4 focus:outline-none focus:border-primary appearance-none"
              >
                <option value="all">All Status</option>
                {Object.values(CLAIM_STATUS).map(status => (
                  <option key={status} value={status}>{status}</option>
                ))}
              </select>
            </div>

            {/* Date Filter */}
            <div className="relative">
              <input
                type="date"
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
                className="w-full bg-background border border-gray-800 rounded-lg py-2 px-4 focus:outline-none focus:border-primary"
              />
            </div>

            {/* Export Button */}
            <Button variant="secondary" className="flex items-center justify-center gap-2">
              <FiDownload />
              Export
            </Button>
          </div>

          {/* Active Filters */}
          {(searchTerm || statusFilter !== 'all' || dateFilter) && (
            <div className="flex items-center gap-2 mt-4 pt-4 border-t border-gray-800">
              <span className="text-sm text-textSecondary">Active filters:</span>
              {searchTerm && (
                <span className="bg-primary/20 text-primary px-3 py-1 rounded-full text-sm">
                  Search: {searchTerm}
                </span>
              )}
              {statusFilter !== 'all' && (
                <span className="bg-primary/20 text-primary px-3 py-1 rounded-full text-sm">
                  Status: {statusFilter}
                </span>
              )}
              {dateFilter && (
                <span className="bg-primary/20 text-primary px-3 py-1 rounded-full text-sm">
                  Date: {dateFilter}
                </span>
              )}
              <button
                onClick={() => {
                  setSearchTerm('');
                  setStatusFilter('all');
                  setDateFilter('');
                }}
                className="text-sm text-danger hover:underline ml-auto"
              >
                Clear all
              </button>
            </div>
          )}
        </div>

        {/* Loading State */}
        {loading ? (
          <div className="bg-surface rounded-xl border border-gray-800 p-12 text-center">
            <div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
            <p className="text-textSecondary">Loading your claims...</p>
          </div>
        ) : (
          /* Claims Table */
          <div className="bg-surface rounded-xl border border-gray-800 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-background/50">
                  <tr className="text-left text-textSecondary text-sm">
                    <th className="px-6 py-4">Claim ID</th>
                    <th className="px-6 py-4">Date</th>
                    <th className="px-6 py-4">Hospital</th>
                    <th className="px-6 py-4">Disease</th>
                    <th className="px-6 py-4">Amount</th>
                    <th className="px-6 py-4">Status</th>
                    <th className="px-6 py-4">Risk Score</th>
                    <th className="px-6 py-4">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {filteredClaims.length > 0 ? (
                    filteredClaims.map((claim) => (
                      <tr 
                        key={claim.id} 
                        className="hover:bg-surface/80 transition-colors"
                      >
                        <td className="px-6 py-4 font-mono">{claim.id}</td>
                        <td className="px-6 py-4 text-textSecondary">{claim.date}</td>
                        <td className="px-6 py-4">{claim.hospital || 'City General Hospital'}</td>
                        <td className="px-6 py-4">{claim.disease || 'General'}</td>
                        <td className="px-6 py-4 font-medium">{claim.amount}</td>
                        <td className="px-6 py-4">
                          <StatusBadge status={claim.status} />
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <div className="w-16 bg-background rounded-full h-2">
                              <div 
                                className={`h-2 rounded-full ${
                                  claim.risk > 70 ? 'bg-danger' : 
                                  claim.risk > 40 ? 'bg-warning' : 'bg-success'
                                }`}
                                style={{ width: `${claim.risk}%` }}
                              ></div>
                            </div>
                            <span className={`text-sm ${
                              claim.risk > 70 ? 'text-danger' : 
                              claim.risk > 40 ? 'text-warning' : 'text-success'
                            }`}>
                              {claim.risk}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <Link 
                              to={`/user/claims/${claim.id}`}
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
                    ))
                  ) : (
                    <tr>
                      <td colSpan="8" className="px-6 py-12 text-center">
                        <div className="text-textSecondary mb-4">No claims found</div>
                        <Link to="/user/submit-claim">
                          <Button>Submit Your First Claim</Button>
                        </Link>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

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

        {/* Floating Action Button to Submit New Claim */}
        <Link to="/user/submit-claim">
          <button className="fixed bottom-8 right-8 w-14 h-14 bg-primary rounded-full shadow-lg shadow-primary/30 flex items-center justify-center hover:bg-primary/90 transition-all hover:scale-110">
            <span className="text-2xl">+</span>
          </button>
        </Link>
      </main>
    </div>
  );
}