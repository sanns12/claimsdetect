import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Button from '../../components/Button';
import StatusBadge from '../../components/StatusBadge';
import { 
  FiActivity, 
  FiClock, 
  FiUser, 
  FiFileText, 
  FiCheckCircle, 
  FiAlertTriangle, 
  FiXCircle,
  FiTrendingUp,
  FiUploadCloud,
  FiUsers,
  FiCalendar,
  FiArrowRight,
  FiBell,
  FiLogOut
} from 'react-icons/fi';
import { CLAIM_STATUS } from '../../utils/constants';
import { getHospitalDashboardStats } from '../../services/dashboard';
import { getHospitalClaims } from '../../services/claims';
import { getCurrentUser, logout } from '../../services/auth';

export default function HospitalDashboard() {
  const navigate = useNavigate();
  const [showLogoutMenu, setShowLogoutMenu] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [hospitalInfo, setHospitalInfo] = useState({
    name: 'City General Hospital',
    id: 'HOSP-001',
    department: 'Main Branch'
  });
  
  const [stats, setStats] = useState({
    totalClaims: 0,
    pendingReview: 0,
    approved: 0,
    flagged: 0,
    fraud: 0,
    totalAmount: '$0',
    avgProcessingTime: '0 days'
  });

  const [recentClaims, setRecentClaims] = useState([]);
  const [departmentStats, setDepartmentStats] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError('');

    try {
      // Get hospital info from user data
      try {
        const userData = await getCurrentUser();
        if (userData) {
          setHospitalInfo({
            name: userData.hospital_name || 'City General Hospital',
            id: userData.hospital_id || 'HOSP-001',
            department: userData.department || 'Main Branch'
          });
        }
      } catch (userError) {
        console.log('Could not fetch user info, using default');
        setHospitalInfo({
          name: 'City General Hospital',
          id: 'HOSP-001', 
          department: 'Main Branch'
        });
      }

      // Get dashboard stats
      const statsData = await getHospitalDashboardStats();
      setStats({
        totalClaims: statsData.total_claims || 156,
        pendingReview: statsData.pending_review || 23,
        approved: statsData.approved || 98,
        flagged: statsData.flagged || 28,
        fraud: statsData.fraud || 7,
        totalAmount: statsData.total_amount || '$1.2M',
        avgProcessingTime: statsData.avg_processing_time || '2.4 days'
      });

      // Get recent claims - handle gracefully if endpoint doesn't exist
      try {
        const claimsData = await getHospitalClaims({ limit: 5 });
        setRecentClaims(claimsData.claims || []);
      } catch (claimsError) {
        console.log('Claims endpoint not available, using fallback data');
        setRecentClaims([]);
      }

      // Get department stats (mock for now, would come from API)
      setDepartmentStats([
        { dept: 'Emergency', claims: 45, approved: 32, flagged: 8, fraud: 2 },
        { dept: 'Cardiology', claims: 38, approved: 28, flagged: 7, fraud: 1 },
        { dept: 'Orthopedics', claims: 32, approved: 22, flagged: 6, fraud: 2 },
        { dept: 'Pediatrics', claims: 28, approved: 24, flagged: 3, fraud: 0 },
        { dept: 'Oncology', claims: 13, approved: 8, flagged: 4, fraud: 2 }
      ]);

    } catch (err) {
      console.error('Failed to load dashboard:', err);
      setError('Failed to load dashboard data. Please refresh.');
      
      // Fallback to mock data
      setStats({
        totalClaims: 156,
        pendingReview: 23,
        approved: 98,
        flagged: 28,
        fraud: 7,
        totalAmount: '$1.2M',
        avgProcessingTime: '2.4 days'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // Mock data for chart
  const weeklyData = [45, 52, 38, 65, 48, 72, 58];
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  if (loading) {
    return (
      <div className="min-h-screen bg-background text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-textSecondary">Loading hospital dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-white">
      {/* Header */}
      <header className="bg-surface/50 backdrop-blur-sm border-b border-gray-800 sticky top-0 z-50">
        <div className="px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-8">
            <Link to="/hospital/dashboard" className="text-2xl font-bold text-primary">
              InsureVerify
            </Link>
            <span className="text-sm bg-primary/20 text-primary px-3 py-1 rounded-full">
              Hospital Portal
            </span>
          </div>

          <div className="flex items-center gap-4">
            {/* Quick Stats */}
            <div className="hidden md:flex items-center gap-4 text-sm">
              <div className="flex items-center gap-2">
                <FiClock className="text-textSecondary" />
                <span>{stats.avgProcessingTime}</span>
              </div>
              <div className="w-px h-4 bg-gray-800"></div>
              <div className="flex items-center gap-2">
                <FiActivity className="text-textSecondary" />
                <span>{stats.pendingReview} pending</span>
              </div>
            </div>

            {/* Notification Bell */}
            <button className="relative p-2 hover:bg-surface rounded-lg transition-colors">
              <FiBell className="text-textSecondary text-xl" />
              {stats.flagged > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 bg-danger rounded-full"></span>
              )}
            </button>

            {/* Hospital Profile */}
            <div className="relative">
              <button 
                onClick={() => setShowLogoutMenu(!showLogoutMenu)}
                className="flex items-center gap-3 bg-surface hover:bg-surface/80 rounded-lg pl-3 pr-2 py-2 transition-colors border border-gray-800"
              >
                <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
                  <FiUsers className="text-primary" />
                </div>
                <span className="hidden md:block">{hospitalInfo.name}</span>
              </button>

              {/* Logout Dropdown */}
              {showLogoutMenu && (
                <div className="absolute right-0 mt-2 w-56 bg-surface border border-gray-800 rounded-lg shadow-xl overflow-hidden">
                  <div className="p-3 border-b border-gray-800">
                    <p className="text-sm font-medium">{hospitalInfo.name}</p>
                    <p className="text-xs text-textSecondary">ID: {hospitalInfo.id}</p>
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

        {/* Welcome Section */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Hospital Dashboard</h1>
            <p className="text-textSecondary mt-1">{hospitalInfo.name} • {hospitalInfo.department}</p>
          </div>
          <div className="flex gap-3">
            <Link to="/hospital/submit-claim">
              <Button className="flex items-center gap-2">
                <FiUploadCloud />
                Submit Claim
              </Button>
            </Link>
            <Link to="/hospital/claims">
              <Button variant="secondary" className="flex items-center gap-2">
                <FiFileText />
                View All Claims
              </Button>
            </Link>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="bg-surface p-6 rounded-xl border border-gray-800">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-textSecondary text-sm">Total Claims</p>
                <p className="text-3xl font-bold mt-2">{stats.totalClaims}</p>
                <p className="text-xs text-textSecondary mt-2">This month</p>
              </div>
              <div className="p-3 bg-primary/20 rounded-lg">
                <FiFileText className="text-primary text-xl" />
              </div>
            </div>
          </div>

          <div className="bg-surface p-6 rounded-xl border border-gray-800">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-textSecondary text-sm">Total Amount</p>
                <p className="text-3xl font-bold mt-2 text-success">{stats.totalAmount}</p>
                <p className="text-xs text-textSecondary mt-2">Processed</p>
              </div>
              <div className="p-3 bg-success/20 rounded-lg">
                <FiTrendingUp className="text-success text-xl" />
              </div>
            </div>
          </div>

          <div className="bg-surface p-6 rounded-xl border border-gray-800">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-textSecondary text-sm">Flagged/Fraud</p>
                <p className="text-3xl font-bold mt-2">
                  <span className="text-warning">{stats.flagged}</span>
                  <span className="text-textSecondary mx-1">/</span>
                  <span className="text-danger">{stats.fraud}</span>
                </p>
                <p className="text-xs text-textSecondary mt-2">Need attention</p>
              </div>
              <div className="p-3 bg-warning/20 rounded-lg">
                <FiAlertTriangle className="text-warning text-xl" />
              </div>
            </div>
          </div>

          <div className="bg-surface p-6 rounded-xl border border-gray-800">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-textSecondary text-sm">Approval Rate</p>
                <p className="text-3xl font-bold mt-2">
                  {Math.round((stats.approved / stats.totalClaims) * 100)}%
                </p>
                <p className="text-xs text-success mt-2">↑ 8% from last month</p>
              </div>
              <div className="p-3 bg-info/20 rounded-lg">
                <FiCheckCircle className="text-info text-xl" />
              </div>
            </div>
          </div>
        </div>

        {/* Charts and Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Weekly Activity Chart */}
          <div className="lg:col-span-2 bg-surface rounded-xl border border-gray-800 p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="font-bold">Weekly Claim Submissions</h2>
              <select className="bg-background border border-gray-800 rounded-lg px-3 py-1 text-sm">
                <option>Last 7 days</option>
                <option>Last 30 days</option>
                <option>This month</option>
              </select>
            </div>
            <div className="h-48 flex items-end justify-between gap-2">
              {weeklyData.map((value, index) => (
                <div key={index} className="flex flex-col items-center gap-2 w-full">
                  <div 
                    className="w-full bg-primary/20 rounded-t-lg"
                    style={{ height: `${value}px` }}
                  >
                    <div 
                      className="w-full bg-primary rounded-t-lg h-full opacity-75 hover:opacity-100 transition-opacity"
                      style={{ height: `${value}%` }}
                    ></div>
                  </div>
                  <span className="text-xs text-textSecondary">{days[index]}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Department Summary */}
          <div className="bg-surface rounded-xl border border-gray-800 p-6">
            <h2 className="font-bold mb-4">Department Overview</h2>
            <div className="space-y-4">
              {departmentStats.map((dept, index) => (
                <div key={index}>
                  <div className="flex justify-between text-sm mb-1">
                    <span>{dept.dept}</span>
                    <span className="text-textSecondary">{dept.claims} claims</span>
                  </div>
                  <div className="flex gap-1 h-2">
                    <div 
                      className="bg-success rounded-l-full" 
                      style={{ width: `${(dept.approved / dept.claims) * 100}%` }}
                    ></div>
                    <div 
                      className="bg-warning" 
                      style={{ width: `${(dept.flagged / dept.claims) * 100}%` }}
                    ></div>
                    <div 
                      className="bg-danger rounded-r-full" 
                      style={{ width: `${(dept.fraud / dept.claims) * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Claims Table */}
        <div className="bg-surface rounded-xl border border-gray-800 overflow-hidden">
          <div className="p-6 border-b border-gray-800 flex justify-between items-center">
            <h2 className="font-bold">Recent Claims</h2>
            <Link to="/hospital/claims" className="text-primary hover:underline text-sm flex items-center gap-1">
              View All <FiArrowRight />
            </Link>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-background/50">
                <tr className="text-left text-textSecondary text-sm">
                  <th className="px-6 py-4">Claim ID</th>
                  <th className="px-6 py-4">Patient</th>
                  <th className="px-6 py-4">Date</th>
                  <th className="px-6 py-4">Amount</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Risk</th>
                  <th className="px-6 py-4">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {recentClaims.length > 0 ? (
                  recentClaims.map((claim) => (
                    <tr key={claim.id} className="hover:bg-surface/80 transition-colors">
                      <td className="px-6 py-4 font-mono">{claim.id}</td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <FiUser className="text-textSecondary" />
                          {claim.patientName}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-textSecondary">{claim.date}</td>
                      <td className="px-6 py-4">{claim.amount}</td>
                      <td className="px-6 py-4">
                        <StatusBadge status={claim.status} />
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          claim.risk > 70 ? 'bg-danger/20 text-danger' :
                          claim.risk > 40 ? 'bg-warning/20 text-warning' :
                          'bg-success/20 text-success'
                        }`}>
                          {claim.risk}% Risk
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <Link 
                          to={`/hospital/claims/${claim.id}`}
                          className="text-primary hover:underline text-sm"
                        >
                          View Details
                        </Link>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="7" className="px-6 py-8 text-center text-textSecondary">
                      No recent claims found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <Link to="/hospital/submit-claim" className="bg-surface/50 hover:bg-surface border border-gray-800 rounded-xl p-4 transition-colors">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-primary/20 rounded-lg">
                <FiUploadCloud className="text-primary text-xl" />
              </div>
              <div>
                <h3 className="font-bold">Submit New Claim</h3>
                <p className="text-sm text-textSecondary">Individual or bulk upload</p>
              </div>
            </div>
          </Link>

          <div className="bg-surface/50 border border-gray-800 rounded-xl p-4">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-warning/20 rounded-lg">
                <FiAlertTriangle className="text-warning text-xl" />
              </div>
              <div>
                <h3 className="font-bold">Pending Reviews</h3>
                <p className="text-sm text-textSecondary">{stats.pendingReview} claims need attention</p>
              </div>
            </div>
          </div>

          <div className="bg-surface/50 border border-gray-800 rounded-xl p-4">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-success/20 rounded-lg">
                <FiCalendar className="text-success text-xl" />
              </div>
              <div>
                <h3 className="font-bold">Monthly Report</h3>
                <p className="text-sm text-textSecondary">Download March summary</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}