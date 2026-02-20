import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Button from '../../components/Button';
import StatusBadge from '../../components/StatusBadge';
import { 
  FiFileText, FiCheckCircle, FiAlertTriangle, FiXCircle, 
  FiTrendingUp, FiClock, FiLogOut, FiUser, FiBell 
} from 'react-icons/fi';
import { CLAIM_STATUS } from '../../utils/constants';

export default function UserDashboard() {
  const navigate = useNavigate();
  const [showLogoutMenu, setShowLogoutMenu] = useState(false);

  const [stats] = useState({
    total: 24,
    approved: 18,
    flagged: 4,
    fraud: 2,
    pending: 6
  });

  const [recentClaims] = useState([
    { id: 'CLM001', date: '2024-03-15', amount: '$5,200', status: CLAIM_STATUS.APPROVED, risk: 23 },
    { id: 'CLM002', date: '2024-03-14', amount: '$12,500', status: CLAIM_STATUS.AI_PROCESSING, risk: 67 },
    { id: 'CLM003', date: '2024-03-13', amount: '$3,800', status: CLAIM_STATUS.FLAGGED, risk: 82 },
    { id: 'CLM004', date: '2024-03-12', amount: '$8,900', status: CLAIM_STATUS.SUBMITTED, risk: 45 },
    { id: 'CLM005', date: '2024-03-11', amount: '$15,200', status: CLAIM_STATUS.APPROVED, risk: 18 },
  ]);

  const monthlyData = [65, 78, 52, 84, 93, 71, 88, 95, 67, 82, 91, 77];
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  const handleLogout = () => {
    // Clear any auth tokens/session here
    localStorage.removeItem('user');
    sessionStorage.removeItem('user');
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-background text-white">
      {/* Header with Logout */}
      <header className="bg-surface/50 backdrop-blur-sm border-b border-gray-800 sticky top-0 z-50">
        <div className="px-6 py-4 flex justify-between items-center">
          {/* Left side - Logo and page title */}
          <div className="flex items-center gap-8">
            <Link to="/user/dashboard" className="text-2xl font-bold text-primary">
              InsureVerify
            </Link>
            <span className="text-textSecondary text-sm hidden md:block">
              User Dashboard
            </span>
          </div>

          {/* Right side - Notifications and Profile/Logout */}
          <div className="flex items-center gap-4">
            {/* Notification Bell */}
            <button className="relative p-2 hover:bg-surface rounded-lg transition-colors">
              <FiBell className="text-textSecondary text-xl" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-danger rounded-full"></span>
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
              <span className="hidden md:block">
  {JSON.parse(localStorage.getItem('user') || sessionStorage.getItem('user') || '{"name":"User"}').name}
</span>
                <FiClock className="text-textSecondary text-sm rotate-90" />
              </button>

              {/* Logout Dropdown */}
              {showLogoutMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-surface border border-gray-800 rounded-lg shadow-xl overflow-hidden">
                  <div className="p-3 border-b border-gray-800">
                    <p className="text-sm font-medium">{JSON.parse(localStorage.getItem('user') || sessionStorage.getItem('user') || '{"name":"User"}').name}</p>
                    <p className="text-xs text-textSecondary">john.doe@example.com</p>
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
        {/* Welcome Message */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Welcome back, John</h1>
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
            <div className="mt-4 text-xs text-textSecondary">
              <span className="text-success">↑ 12%</span> from last month
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
            <div className="mt-4 text-xs text-textSecondary">
              <span className="text-success">↑ 8%</span> from last month
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
            <div className="mt-4 text-xs text-textSecondary">
              <span className="text-danger">↑ 2</span> new flags
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
            <div className="mt-4 text-xs text-textSecondary">
              <span className="text-success">↓ 1</span> resolved
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
            <div className="mt-4 text-xs text-textSecondary">
              <span className="text-warning">3</span> need attention
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
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

          <div className="bg-surface p-6 rounded-xl border border-gray-800">
            <h3 className="font-bold mb-6">Status Distribution</h3>
            <div className="flex items-center justify-center mb-6">
              <div className="relative w-40 h-40">
                <div 
                  className="w-full h-full rounded-full"
                  style={{
                    background: `conic-gradient(
                      #10B981 0deg 270deg,
                      #F59E0B 270deg 330deg,
                      #EF4444 330deg 360deg
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
                {recentClaims.map((claim) => (
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
                ))}
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