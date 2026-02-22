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
import { getClaims, deleteClaim } from '../../services/claims';
import { formatClaimFromApi } from '../../utils/apiHelpers';

export default function UserClaimList() {
  const location = useLocation();
  //const successMessage = location.state?.message;

  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [dateFilter] = useState('');
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [, setError] = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [claimToDelete, setClaimToDelete] = useState(null);
  const [deleteInProgress, setDeleteInProgress] = useState(false);

  useEffect(() => {
    fetchClaims();
  }, []);

  const fetchClaims = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await getClaims();
      const formatted = response.claims.map(formatClaimFromApi);
      setClaims(formatted);
      localStorage.setItem('userClaims', JSON.stringify(formatted));
    } catch (err) {
      console.error('Fetch failed:', err);
      setError('Failed to load claims. Showing saved data.');
      const stored = JSON.parse(localStorage.getItem('userClaims') || '[]');
      setClaims(stored);
    } finally {
      setLoading(false);
    }
  };

  const filteredClaims = claims.filter(claim => {
    const matchesSearch =
      searchTerm === '' ||
      claim.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (claim.disease && claim.disease.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (claim.patientName && claim.patientName.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesStatus = statusFilter === 'all' || claim.status === statusFilter;
    const matchesDate = !dateFilter || claim.date === dateFilter;

    return matchesSearch && matchesStatus && matchesDate;
  });

  const handleDeleteClick = (claim) => {
    setClaimToDelete(claim);
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!claimToDelete) return;

    setDeleteInProgress(true);

    try {
      await deleteClaim(claimToDelete.id);
      const updated = claims.filter(c => c.id !== claimToDelete.id);
      setClaims(updated);
      localStorage.setItem('userClaims', JSON.stringify(updated));
      setShowDeleteModal(false);
      setClaimToDelete(null);
    } catch (err) {
      console.error('Delete failed:', err);
      setError('Failed to delete claim.');
    } finally {
      setDeleteInProgress(false);
    }
  };

  const exportToCSV = () => {
    const headers = ['Claim ID', 'Date', 'Patient Name', 'Disease', 'Amount', 'Status'];
    const rows = filteredClaims.map(claim => [
      claim.id,
      claim.date,
      claim.patientName,
      claim.disease,
      claim.amount,
      claim.status
    ]);

    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `my-claims-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  return (
    <div className="min-h-screen bg-background text-white">

      {/* Delete Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-surface rounded-xl border border-gray-800 max-w-md w-full p-6">
            <div className="flex items-center gap-3 text-danger mb-4">
              <FiAlertCircle className="text-3xl" />
              <h2 className="text-xl font-bold">Delete Claim</h2>
            </div>

            <p className="mb-6">
              Delete claim <span className="font-mono text-primary">{claimToDelete?.id}</span>?
            </p>

            <div className="flex gap-3 justify-end">
              <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
                Cancel
              </Button>
              <Button variant="danger" onClick={confirmDelete}>
                {deleteInProgress ? 'Deleting...' : 'Delete'}
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <header className="bg-surface/50 border-b border-gray-800 sticky top-0 z-40">
        <div className="px-6 py-4 flex items-center gap-4">
          <Link to="/user/dashboard">
            <FiArrowLeft />
          </Link>
          <h1 className="text-xl font-bold">My Claims</h1>
        </div>
      </header>

      <main className="p-6">

        {/* Filters */}
        <div className="bg-surface rounded-xl border border-gray-800 p-4 mb-6">
          <div className="grid md:grid-cols-3 gap-4">

            <div className="relative">
              <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-textSecondary" />
              <input
                type="text"
                placeholder="Search claims..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-background border border-gray-800 rounded-lg py-2 pl-10 pr-4"
              />
            </div>

            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-background border border-gray-800 rounded-lg py-2 px-4"
            >
              <option value="all">All Status</option>
              {Object.values(CLAIM_STATUS).map(status => (
                <option key={status} value={status}>{status}</option>
              ))}
            </select>

            <Button variant="secondary" onClick={exportToCSV}>
              <FiDownload className="mr-2" /> Export
            </Button>

          </div>
        </div>

        {/* Table */}
        {loading ? (
          <div className="text-center py-12">Loading...</div>
        ) : (
          <div className="bg-surface rounded-xl border border-gray-800 overflow-hidden">
            <table className="w-full">
              <thead className="bg-background/50 text-sm text-textSecondary">
                <tr>
                  <th className="px-6 py-4 text-left">Claim ID</th>
                  <th className="px-6 py-4 text-left">Date</th>
                  <th className="px-6 py-4 text-left">Patient Name</th>
                  <th className="px-6 py-4 text-left">Disease</th>
                  <th className="px-6 py-4 text-left">Amount</th>
                  <th className="px-6 py-4 text-left">Status</th>
                  <th className="px-6 py-4 text-left">Actions</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-gray-800">
                {filteredClaims.length > 0 ? (
                  filteredClaims.map(claim => (
                    <tr key={claim.id} className="hover:bg-surface/80">
                      <td className="px-6 py-4 font-mono">{claim.id}</td>
                      <td className="px-6 py-4">{claim.date}</td>
                      <td className="px-6 py-4">{claim.patientName}</td>
                      <td className="px-6 py-4">{claim.disease}</td>
                      <td className="px-6 py-4">{claim.amount}</td>
                      <td className="px-6 py-4">
                        <StatusBadge status={claim.status} />
                      </td>
                      <td className="px-6 py-4 flex gap-2">
                        <Link to={`/user/claims/${claim.id}`}>
                          <FiEye />
                        </Link>
                        <button onClick={() => handleDeleteClick(claim)}>
                          <FiTrash2 />
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="7" className="px-6 py-12 text-center">
                      No claims found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

      </main>
    </div>
  );
}