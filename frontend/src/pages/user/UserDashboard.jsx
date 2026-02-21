import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Button from '../../components/Button';
import StatusBadge from '../../components/StatusBadge';
import { 
  FiFileText, FiCheckCircle, FiAlertTriangle, FiXCircle, 
  FiTrendingUp, FiClock, FiLogOut, FiUser, FiBell 
} from 'react-icons/fi';
import { CLAIM_STATUS } from '../../utils/constants';
import { getUserDashboardStats } from '../../services/dashboard';
import { getUserClaims } from '../../services/claims';
import { getCurrentUser, logout } from '../../services/auth';

export default function UserDashboard() {
  const navigate = useNavigate();
  const [showLogoutMenu, setShowLogoutMenu] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [stats, setStats] = useState({
    total: 0,
    approved: 0,
    flagged: 0,
    fraud: 0,
    pending: 0
  });
  const [recentClaims, setRecentClaims] = useState([]);
  const [user, setUser] = useState({ name: 'User', email: '' });

  // Load dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      setError('');
      
      try {
        // Get user info
        try {
          const userData = await getCurrentUser();
          if (userData) {
            setUser(userData);
          }
        } catch (userError) {
          console.log('Could not fetch user info, using stored data', userError);
          const storedUser = JSON.parse(localStorage.getItem('user') || '{}');
          if (storedUser.email) {
            setUser({ name: storedUser.full_name || 'User', email: storedUser.email });
          }
        }

        // Get dashboard stats
        const statsData = await getUserDashboardStats();
        setStats({
          total: statsData.total_claims || 0,
          approved: statsData.approved || 0,
          flagged: statsData.flagged || 0, 
          fraud: statsData.fraud || 0,
          pending: statsData.pending_review || 0
        });

        // Get recent claims - handle gracefully if endpoint doesn't exist
        try {
          const claimsData = await getUserClaims({ limit: 5 });
          setRecentClaims(claimsData.claims || []);
        } catch (claimsError) {
          console.log('Claims endpoint not available, using fallback data', claimsError);
          setRecentClaims([]);
        }
        
      } catch (err) {
        console.error('Failed to load dashboard:', err);
        setError('Failed to load dashboard data. Please refresh.');
        
        // Fallback to localStorage if API fails
        const storedClaims = JSON.parse(localStorage.getItem('userClaims') || '[]');
        setRecentClaims(storedClaims.slice(0, 5));
        setStats({
          total: storedClaims.length,
          approved: storedClaims.filter(c => c.status === CLAIM_STATUS.APPROVED).length,
          flagged: storedClaims.filter(c => c.status === CLAIM_STATUS.FLAGGED).length,
          fraud: storedClaims.filter(c => c.status === CLAIM_STATUS.FRAUD).length,
          pending: storedClaims.filter(c => 
            [CLAIM_STATUS.SUBMITTED, CLAIM_STATUS.AI_PROCESSING].includes(c.status)
          ).length
        });
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Mock data for charts (still can be static)
  const monthlyData = [65, 78, 52, 84, 93, 71, 88, 95, 67, 82, 91, 77];
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  if (loading) {
    return (
      <div className="min-h-screen bg-background text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-textSecondary">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-white">
      {/* Header with Logout */}
      <header className="bg-surface/50 backdrop-blur-sm border-b border-gray-800 sticky top-0 z-50">
        <div className="px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-8">
            <Link to="/user/dashboard" className="text-2xl font-bold text-primary">
              InsureVerify
            </Link>
            <span className="text-textSecondary text-sm hidden md:block">
              User Dashboard
            </span>
          </div>

          <div className="flex items-center gap-4">
            {/* Notification Bell */}
            <button className="relative p-2 hover:bg-surface rounded-lg transition-colors">
              <FiBell className="text-textSecondary text-xl" />
              {stats.flagged > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 bg-danger rounded-full"></span>
              )}
            </button>

            {/* User Menu with Logout */}
            <div className="relative">
              <button 
                onClick={() => setShowLogoutMenu(!showLogoutMenu)}
                className="flex items-center gap-3 bg-surface hover:bg-surface/80 rounded-lg pl-3 pr-2 py-2 transition-colors border border-gray-800"
              >
                <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
                  <FiUser className="text-primary" />
                </div>
                <span className="hidden md:block">{user.name || 'User'}</span>
                <FiClock className="text-textSecondary text-sm rotate-90" />
              </button>

              {/* Logout Dropdown */}
              {showLogoutMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-surface border border-gray-800 rounded-lg shadow-xl overflow-hidden">
                  <div className="p-3 border-b border-gray-800">
                    <p className="text-sm font-medium">{user.name || 'User'}</p>
                    <p className="text-xs text-textSecondary">{user.email || 'user@example.com'}</p>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-danger/10 transition-colors text-danger"
                  >
                    <FiLogOut />
                    <span>Logout</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="p-6">
        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-danger/10 border border-danger/30 text-danger px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Welcome Message */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Welcome back, {user.name || 'User'}</h1>
          <p className="text-textSecondary mt-1">Track and manage your insurance claims</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
          <div className="bg-surface p-6 rounded-xl border border-gray-800">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-textSecondary text-sm">Total Claims</p>
                <p className="text-3xl font-bold mt-2">{stats.total}</p>
              </div>
              <div className="p-3 bg-primary/20 rounded-lg">
                <FiFileText className="text-primary text-xl" />
              </div>
            </div>
          </div>

          <div className="bg-surface p-6 rounded-xl border border-gray-800">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-textSecondary text-sm">Approved</p>
                <p className="text-3xl font-bold mt-2 text-success">{stats.approved}</p>
              </div>
              <div className="p-3 bg-success/20 rounded-lg">
                <FiCheckCircle className="text-success text-xl" />
              </div>
            </div>
          </div>

          <div className="bg-surface p-6 rounded-xl border border-gray-800">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-textSecondary text-sm">Flagged</p>
                <p className="text-3xl font-bold mt-2 text-warning">{stats.flagged}</p>
              </div>
              <div className="p-3 bg-warning/20 rounded-lg">
                <FiAlertTriangle className="text-warning text-xl" />
              </div>
            </div>
          </div>

          <div className="bg-surface p-6 rounded-xl border border-gray-800">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-textSecondary text-sm">Fraud</p>
                <p className="text-3xl font-bold mt-2 text-danger">{stats.fraud}</p>
              </div>
              <div className="p-3 bg-danger/20 rounded-lg">
                <FiXCircle className="text-danger text-xl" />
              </div>
            </div>
          </div>

          <div className="bg-surface p-6 rounded-xl border border-gray-800">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-textSecondary text-sm">Pending</p>
                <p className="text-3xl font-bold mt-2 text-info">{stats.pending}</p>
              </div>
              <div className="p-3 bg-info/20 rounded-lg">
                <FiTrendingUp className="text-info text-xl" />
              </div>
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Bar Chart - Claims by Month */}
          <div className="lg:col-span-2 bg-surface p-6 rounded-xl border border-gray-800">
            <div className="flex justify-between items-center mb-6">
              <h3 className="font-bold">Claims Activity</h3>
              <select className="bg-background border border-gray-800 rounded-lg px-3 py-1 text-sm">
                <option>Last 12 months</option>
                <option>Last 6 months</option>
                <option>Last 30 days</option>
              </select>
            </div>
            <div className="h-64 flex items-end justify-between gap-2">
              {monthlyData.map((value, index) => (
                <div key={index} className="flex flex-col items-center gap-2 w-full">
                  <div 
                    className="w-full bg-primary/20 rounded-t-lg relative group"
                    style={{ height: `${value * 2}px` }}
                  >
                    <div 
                      className="absolute bottom-0 w-full bg-primary rounded-t-lg transition-all duration-300 group-hover:bg-primary/80"
                      style={{ height: `${value}%` }}
                    ></div>
                  </div>
                  <span className="text-xs text-textSecondary">{months[index]}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Pie Chart - Status Distribution */}
          <div className="bg-surface p-6 rounded-xl border border-gray-800">
            <h3 className="font-bold mb-6">Status Distribution</h3>
            <div className="flex items-center justify-center mb-6">
              <div className="relative w-40 h-40">
                <div 
                  className="w-full h-full rounded-full"
                  style={{
                    background: `conic-gradient(
                      #10B981 0deg ${stats.approved / stats.total * 360}deg,
                      #F59E0B ${stats.approved / stats.total * 360}deg ${(stats.approved + stats.flagged) / stats.total * 360}deg,
                      #EF4444 ${(stats.approved + stats.flagged) / stats.total * 360}deg 360deg
                    )`
                  }}
                ></div>
                <div className="absolute inset-2 bg-surface rounded-full flex items-center justify-center">
                  <span className="text-2xl font-bold">{stats.total}</span>
                </div>
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-success"></div>
                  <span className="text-textSecondary">Approved</span>
                </div>
                <span className="font-bold">{stats.approved}</span>
              </div>
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-warning"></div>
                  <span className="text-textSecondary">Flagged</span>
                </div>
                <span className="font-bold">{stats.flagged}</span>
              </div>
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-danger"></div>
                  <span className="text-textSecondary">Fraud</span>
                </div>
                <span className="font-bold">{stats.fraud}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Claims Table */}
        <div className="bg-surface rounded-xl border border-gray-800 overflow-hidden">
          <div className="p-6 border-b border-gray-800 flex justify-between items-center">
            <h3 className="font-bold">Recent Claims</h3>
            <Link to="/user/claims" className="text-primary hover:underline text-sm">
              View All Claims →
            </Link>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-background/50">
                <tr className="text-left text-textSecondary text-sm">
                  <th className="px-6 py-4">Claim ID</th>
                  <th className="px-6 py-4">Date</th>
                  <th className="px-6 py-4">Amount</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Risk Score</th>
                  <th className="px-6 py-4">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {recentClaims.length > 0 ? (
                  recentClaims.map((claim) => (
                    <tr key={claim.id} className="hover:bg-surface/80 transition-colors">
                      <td className="px-6 py-4 font-mono">{claim.id}</td>
                      <td className="px-6 py-4 text-textSecondary">{claim.date}</td>
                      <td className="px-6 py-4">{claim.amount}</td>
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
                        <Link 
                          to={`/user/claims/${claim.id}`}
                          className="text-primary hover:underline text-sm"
                        >
                          View Details →
                        </Link>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="6" className="px-6 py-8 text-center text-textSecondary">
                      No claims yet. Submit your first claim!
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Floating Action Button */}
        <Link to="/user/submit-claim">
          <button className="fixed bottom-8 right-8 w-14 h-14 bg-primary rounded-full shadow-lg shadow-primary/30 flex items-center justify-center hover:bg-primary/90 transition-all hover:scale-110">
            <span className="text-2xl">+</span>
          </button>
        </Link>
      </main>
    </div>
  );
}