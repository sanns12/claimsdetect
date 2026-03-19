import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Button from '../../components/Button';
import StatusBadge from '../../components/StatusBadge';
import {
  FiFileText, FiCheckCircle, FiAlertTriangle, FiXCircle,
  FiTrendingUp, FiClock, FiLogOut, FiUser, FiBell
} from 'react-icons/fi';
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

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError('');

        // Get user
        const storedUser = JSON.parse(localStorage.getItem('user') || '{}');
        if (storedUser.email) {
          setUser({
            name: storedUser.full_name || storedUser.name || 'User',
            email: storedUser.email
          });
        }

        // Fetch stats
        const statsData = await getUserDashboardStats();

        setStats({
          total: statsData.total_claims || 0,
          approved: statsData.approved || 0,
          flagged: statsData.flagged || 0,
          fraud: statsData.fraud || 0,
          pending: statsData.pending_review || 0
        });

        // Fetch recent claims
        const claimsData = await getUserClaims({ limit: 5 });
        setRecentClaims(claimsData.claims || []);

      } catch (err) {
        console.error('Dashboard load failed:', err);
        setError('Failed to load dashboard data.');
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

  const safeTotal = stats.total || 1; // prevents division by zero

  if (loading) {
    return (
      <div className="min-h-screen bg-background text-white flex items-center justify-center">
        <div className="animate-spin w-12 h-12 border-4 border-primary border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-white">

      {/* HEADER */}
      <header className="bg-surface/50 border-b border-gray-800 sticky top-0 z-50">
        <div className="px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-6">
            <Link to="/user/dashboard" className="text-2xl font-bold text-primary">
              InsureVerify
            </Link>
            <span className="text-textSecondary text-sm hidden md:block">
              User Dashboard
            </span>
          </div>

          <div className="flex items-center gap-4">
            <button className="relative p-2 hover:bg-surface rounded-lg">
              <FiBell />
              {stats.flagged > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 bg-danger rounded-full"></span>
              )}
            </button>

            <div className="relative">
              <button
                onClick={() => setShowLogoutMenu(!showLogoutMenu)}
                className="flex items-center gap-3 bg-surface rounded-lg px-3 py-2 border border-gray-800"
              >
                <FiUser />
                <span>{user.name}</span>
              </button>

              {showLogoutMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-surface border border-gray-800 rounded-lg">
                  <button
                    onClick={handleLogout}
                    className="w-full px-4 py-3 text-left text-danger hover:bg-danger/10"
                  >
                    Logout
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* MAIN */}
      <Link to="/user/submit-claim">
        <button className="fixed bottom-8 right-8 w-14 h-14 bg-primary rounded-full shadow-lg shadow-primary/30 flex items-center justify-center hover:bg-primary/90 transition-all hover:scale-110">
          <span className="text-2xl">+</span>
        </button>
      </Link>
      <main className="p-6">

        {error && (
          <div className="mb-6 bg-danger/10 border border-danger/30 text-danger px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        <div className="mb-8">
          <h1 className="text-3xl font-bold">Welcome back, {user.name}</h1>
          <p className="text-textSecondary">Track and manage your insurance claims</p>
        </div>

        {/* STATS CARDS */}
        <div className="grid md:grid-cols-5 gap-4 mb-8">
          <StatCard title="Total Claims" value={stats.total} icon={<FiFileText />} />
          <StatCard title="Approved" value={stats.approved} icon={<FiCheckCircle />} color="text-success" />
          <StatCard title="Flagged" value={stats.flagged} icon={<FiAlertTriangle />} color="text-warning" />
          <StatCard title="Fraud" value={stats.fraud} icon={<FiXCircle />} color="text-danger" />
          <StatCard title="Pending" value={stats.pending} icon={<FiTrendingUp />} color="text-info" />
        </div>

        {/* PIE CHART */}
        <div className="bg-surface p-6 rounded-xl border border-gray-800 mb-8">
          <h3 className="font-bold mb-6">Status Distribution</h3>
          <div className="relative w-40 h-40 mx-auto">
            <div
              className="w-full h-full rounded-full"
              style={{
                background: `conic-gradient(
                  #10B981 0deg ${(stats.approved / safeTotal) * 360}deg,
                  #F59E0B ${(stats.approved / safeTotal) * 360}deg ${((stats.approved + stats.flagged) / safeTotal) * 360}deg,
                  #EF4444 ${((stats.approved + stats.flagged) / safeTotal) * 360}deg 360deg
                )`
              }}
            />
            <div className="absolute inset-4 bg-surface rounded-full flex items-center justify-center">
              <span className="text-xl font-bold">{stats.total}</span>
            </div>
          </div>
        </div>

        {/* RECENT CLAIMS (NO RISK SCORE FOR USER) */}
        <div className="bg-surface rounded-xl border border-gray-800 overflow-hidden">
          <div className="p-6 border-b border-gray-800 flex justify-between">
            <h3 className="font-bold">Recent Claims</h3>
            <Link to="/user/claims" className="text-primary hover:underline text-sm">
              View All →
            </Link>
          </div>

          <table className="w-full">
            <thead className="bg-background/50 text-textSecondary text-sm">
              <tr>
                <th className="px-6 py-4">Claim ID</th>
                <th className="px-6 py-4">Date</th>
                <th className="px-6 py-4">Amount</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800">
              {recentClaims.length > 0 ? (
                recentClaims.map((claim) => (
                  <tr key={claim.id}>
                    <td className="px-6 py-4 font-mono">{claim.id}</td>
                    <td className="px-6 py-4">{claim.date}</td>
                    <td className="px-6 py-4">{claim.amount}</td>
                    <td className="px-6 py-4">
                      <StatusBadge status={claim.status} />
                    </td>
                    <td className="px-6 py-4">
                      <Link
                        to={`/user/claims/${claim.id}`}
                        className="text-primary hover:underline text-sm"
                      >
                        View →
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="px-6 py-8 text-center text-textSecondary">
                    No claims yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

      </main>
    </div>
  );
}

function StatCard({ title, value, icon, color = 'text-white' }) {
  return (
    <div className="bg-surface p-6 rounded-xl border border-gray-800">
      <div className="flex justify-between">
        <div>
          <p className="text-textSecondary text-sm">{title}</p>
          <p className={`text-3xl font-bold mt-2 ${color}`}>{value}</p>
        </div>
        <div className="p-3 bg-primary/20 rounded-lg">
          {icon}
        </div>
      </div>
    </div>
  );
}