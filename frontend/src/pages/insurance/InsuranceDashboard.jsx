import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Button from '../../components/Button';
import StatusBadge from '../../components/StatusBadge';
import {
  getInsuranceDashboardStats,
  getFraudTrends,
  getRecentAlerts
} from '../../services/dashboard';
import { logout } from '../../services/auth';
import { 
  FiActivity, 
  FiClock, 
  FiFileText, 
  FiCheckCircle, 
  FiAlertTriangle, 
  FiXCircle,
  FiTrendingUp,
  FiUsers,
  FiCalendar,
  FiArrowRight,
  FiBell,
  FiLogOut,
  FiDollarSign,
  FiBarChart2,
  FiPieChart,
  FiShield
} from 'react-icons/fi';
import { CLAIM_STATUS } from '../../utils/constants';

export default function InsuranceDashboard() {
  const navigate = useNavigate();
  const [showLogoutMenu, setShowLogoutMenu] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Stats data
  const [stats, setStats] = useState({
    totalClaims: 0,
    totalValue: 0,
    fraudDetected: 0,
    fraudCases: 0,
    flaggedCases: 0,
    approvedCases: 0,
    pendingReview: 0,
    avgProcessingTime: '0 days',
    accuracyRate: '0%'
  });

  // Fraud trends data
  const [fraudTrends, setFraudTrends] = useState([]);

  // High-risk companies
  const [highRiskCompanies] = useState([
    { name: 'City General Hospital', risk: 78, claims: 45, fraudRate: '12%' },
    { name: 'MediCare Plus Clinic', risk: 65, claims: 32, fraudRate: '8%' },
    { name: 'HealthFirst Medical', risk: 52, claims: 28, fraudRate: '5%' },
    { name: 'QuickCare Center', risk: 48, claims: 56, fraudRate: '4%' },
    { name: 'Premier Health Group', risk: 42, claims: 67, fraudRate: '3%' }
  ]);

  // Recent alerts
  const [recentAlerts, setRecentAlerts] = useState([]);

  // Department risk distribution
  const [riskDistribution] = useState([
    { dept: 'Cardiology', high: 12, medium: 28, low: 45 },
    { dept: 'Orthopedics', high: 8, medium: 32, low: 38 },
    { dept: 'Emergency', high: 15, medium: 25, low: 30 },
    { dept: 'Oncology', high: 5, medium: 18, low: 42 },
    { dept: 'Pediatrics', high: 3, medium: 15, low: 52 }
  ]);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError('');

        const statsData = await getInsuranceDashboardStats();
        setStats({
          totalClaims: statsData.total_claims || 0,
          totalValue: statsData.total_amount || 0,
          fraudDetected: (statsData.total_amount || 0) * (statsData.fraud_probability || 0),
          fraudCases: statsData.fraud_cases || 0,
          flaggedCases: statsData.flagged_cases || 0,
          approvedCases: statsData.approved_cases || 0,
          pendingReview: statsData.pending_review || 0,
          avgProcessingTime: statsData.avg_processing_time || '0 days',
          accuracyRate: statsData.accuracy_rate || '98.5%'
        });

        const trends = await getFraudTrends('month');
        setFraudTrends(Array.isArray(trends) ? trends : []);

        const alerts = await getRecentAlerts(10);
        setRecentAlerts(Array.isArray(alerts) ? alerts : []);
      } catch (err) {
        console.error('Failed to load insurance dashboard:', err);
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

  const getAlertIcon = (type) => {
    switch(type) {
      case 'fraud': return <FiXCircle className="text-danger" />;
      case 'flag': return <FiAlertTriangle className="text-warning" />;
      case 'risk': return <FiTrendingUp className="text-orange-500" />;
      default: return <FiCheckCircle className="text-success" />;
    }
  };

  const getRiskColor = (risk) => {
    if (risk > 70) return 'text-danger';
    if (risk > 50) return 'text-warning';
    if (risk > 30) return 'text-orange-500';
    return 'text-success';
  };

  const getRiskBg = (risk) => {
    if (risk > 70) return 'bg-danger/20';
    if (risk > 50) return 'bg-warning/20';
    if (risk > 30) return 'bg-orange-500/20';
    return 'bg-success/20';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-textSecondary">Loading insurance dashboard...</p>
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
            <Link to="/insurance/dashboard" className="text-2xl font-bold text-primary">
              InsureVerify
            </Link>
            <span className="text-sm bg-primary/20 text-primary px-3 py-1 rounded-full">
              Insurance Admin
            </span>
          </div>

          <div className="flex items-center gap-4">
            {/* Quick Stats */}
            <div className="hidden md:flex items-center gap-4 text-sm">
              <div className="flex items-center gap-2">
                <FiShield className="text-success" />
                <span>{stats.accuracyRate} accuracy</span>
              </div>
              <div className="w-px h-4 bg-gray-800"></div>
              <div className="flex items-center gap-2">
                <FiClock className="text-textSecondary" />
                <span>{stats.avgProcessingTime}</span>
              </div>
            </div>

            {/* Notification Bell */}
            <button className="relative p-2 hover:bg-surface rounded-lg transition-colors">
              <FiBell className="text-textSecondary text-xl" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-danger rounded-full"></span>
            </button>

            {/* Admin Profile */}
            <div className="relative">
              <button 
                onClick={() => setShowLogoutMenu(!showLogoutMenu)}
                className="flex items-center gap-3 bg-surface hover:bg-surface/80 rounded-lg pl-3 pr-2 py-2 transition-colors border border-gray-800"
              >
                <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
                  <FiUsers className="text-primary" />
                </div>
                <span className="hidden md:block">Admin</span>
              </button>

              {/* Logout Dropdown */}
              {showLogoutMenu && (
                <div className="absolute right-0 mt-2 w-56 bg-surface border border-gray-800 rounded-lg shadow-xl overflow-hidden">
                  <div className="p-3 border-b border-gray-800">
                    <p className="text-sm font-medium">Insurance Admin</p>
                    <p className="text-xs text-textSecondary">admin@insureverify.com</p>
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
        {error && (
          <div className="mb-6 bg-danger/10 border border-danger/30 text-danger px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Welcome Section */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Insurance Dashboard</h1>
            <p className="text-textSecondary mt-1">Monitor fraud detection and claims analytics</p>
          </div>
          <div className="flex gap-3">
            <Link to="/insurance/claims">
              <Button variant="secondary" className="flex items-center gap-2">
                <FiFileText />
                View All Claims
              </Button>
            </Link>
            <Link to="/insurance/companies">
              <Button variant="secondary" className="flex items-center gap-2">
                <FiUsers />
                Trust List
              </Button>
            </Link>
          </div>
        </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-surface p-6 rounded-xl border border-gray-800">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-textSecondary text-sm">Total Claims</p>
              <p className="text-3xl font-bold mt-2">{stats.totalClaims}</p>
              <p className="text-xs text-success mt-2">↑ 8% from last month</p>
            </div>
            <div className="p-3 bg-primary/20 rounded-lg">
              <FiFileText className="text-primary text-xl" />
            </div>
          </div>
        </div>

        <div className="bg-surface p-6 rounded-xl border border-gray-800">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-textSecondary text-sm">Total Value</p>
              <p className="text-3xl font-bold mt-2 text-success">${Number(stats.totalValue || 0).toLocaleString()}</p>
              <p className="text-xs text-textSecondary mt-2">Processed claims</p>
            </div>
            <div className="p-3 bg-success/20 rounded-lg">
              <FiDollarSign className="text-success text-xl" />
            </div>
          </div>
        </div>

        <div className="bg-surface p-6 rounded-xl border border-gray-800">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-textSecondary text-sm">Fraud Detected</p>
              <p className="text-3xl font-bold mt-2 text-danger">${Number(stats.fraudDetected || 0).toLocaleString()}</p>
              <p className="text-xs text-danger mt-2">{stats.fraudCases} cases</p>
            </div>
            <div className="p-3 bg-danger/20 rounded-lg">
              <FiXCircle className="text-danger text-xl" />
            </div>
          </div>
        </div>

        <div className="bg-surface p-6 rounded-xl border border-gray-800">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-textSecondary text-sm">Accuracy Rate</p>
              <p className="text-3xl font-bold mt-2 text-info">{stats.accuracyRate}</p>
              <p className="text-xs text-success mt-2">↑ 2% improvement</p>
            </div>
            <div className="p-3 bg-info/20 rounded-lg">
              <FiTrendingUp className="text-info text-xl" />
            </div>
          </div>
        </div>
      </div>

      {/* Charts and Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Fraud Trend Chart */}
        <div className="lg:col-span-2 bg-surface rounded-xl border border-gray-800 p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="font-bold flex items-center gap-2">
              <FiBarChart2 className="text-primary" />
              Fraud Detection Trend
            </h2>
            <select className="bg-background border border-gray-800 rounded-lg px-3 py-1 text-sm">
              <option>Last 6 months</option>
              <option>Last 12 months</option>
              <option>This year</option>
            </select>
          </div>
          <div className="h-48 flex items-end justify-between gap-2">
            {fraudTrends.map((item, index) => (
              <div key={index} className="flex flex-col items-center gap-2 w-full">
                <div 
                  className="w-full bg-danger/20 rounded-t-lg relative group"
                  style={{ height: `${item.amount * 2}px` }}
                >
                  <div 
                    className="absolute bottom-0 w-full bg-danger rounded-t-lg transition-all duration-300 group-hover:bg-danger/80"
                    style={{ height: `${item.amount}%` }}
                  ></div>
                </div>
                <span className="text-xs text-textSecondary">{item.month}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Alerts */}
        <div className="bg-surface rounded-xl border border-gray-800 p-6">
          <h2 className="font-bold flex items-center gap-2 mb-4">
            <FiBell className="text-warning" />
            Recent Alerts
          </h2>
          <div className="space-y-4">
            {recentAlerts.map((alert) => (
              <div key={alert.id} className="flex gap-3">
                <div className="mt-1">
                  {getAlertIcon(alert.type)}
                </div>
                <div className="flex-1">
                  <p className="text-sm">{alert.message}</p>
                  <p className="text-xs text-textSecondary mt-1">{alert.time}</p>
                </div>
                {alert.severity === 'high' && (
                  <span className="text-xs bg-danger/20 text-danger px-2 py-1 rounded-full">
                    Urgent
                  </span>
                )}
              </div>
            ))}
          </div>
          <button className="mt-4 text-sm text-primary hover:underline w-full text-center">
            View All Alerts
          </button>
        </div>
      </div>

      {/* High Risk Companies and Risk Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* High Risk Companies */}
        <div className="bg-surface rounded-xl border border-gray-800 p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="font-bold flex items-center gap-2">
              <FiAlertTriangle className="text-warning" />
              High-Risk Companies
            </h2>
            <Link to="/insurance/companies" className="text-sm text-primary hover:underline">
              View All →
            </Link>
          </div>
          <div className="space-y-4">
            {highRiskCompanies.map((company, index) => (
              <div key={index} className="flex items-center justify-between">
                <div>
                  <p className="font-medium">{company.name}</p>
                  <p className="text-xs text-textSecondary">{company.claims} claims • {company.fraudRate} fraud</p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="w-16 bg-background rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${getRiskBg(company.risk)}`}
                      style={{ width: `${company.risk}%` }}
                    ></div>
                  </div>
                  <span className={`text-sm font-mono ${getRiskColor(company.risk)}`}>
                    {company.risk}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Risk Distribution by Department */}
        <div className="bg-surface rounded-xl border border-gray-800 p-6">
          <h2 className="font-bold flex items-center gap-2 mb-4">
            <FiPieChart className="text-primary" />
            Risk Distribution by Department
          </h2>
          <div className="space-y-4">
            {riskDistribution.map((dept, index) => (
              <div key={index}>
                <div className="flex justify-between text-sm mb-1">
                  <span>{dept.dept}</span>
                  <span className="text-textSecondary">{dept.high + dept.medium + dept.low} claims</span>
                </div>
                <div className="flex gap-1 h-2">
                  <div 
                    className="bg-danger rounded-l-full" 
                    style={{ width: `${(dept.high / (dept.high + dept.medium + dept.low)) * 100}%` }}
                  ></div>
                  <div 
                    className="bg-warning" 
                    style={{ width: `${(dept.medium / (dept.high + dept.medium + dept.low)) * 100}%` }}
                  ></div>
                  <div 
                    className="bg-success rounded-r-full" 
                    style={{ width: `${(dept.low / (dept.high + dept.medium + dept.low)) * 100}%` }}
                  ></div>
                </div>
                <div className="flex gap-4 mt-1 text-xs text-textSecondary">
                  <span className="flex items-center gap-1">
                    <span className="w-2 h-2 bg-danger rounded-full"></span> High: {dept.high}
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="w-2 h-2 bg-warning rounded-full"></span> Medium: {dept.medium}
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="w-2 h-2 bg-success rounded-full"></span> Low: {dept.low}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Status Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-surface/50 rounded-lg border border-gray-800 p-4">
          <p className="text-textSecondary text-sm">Pending Review</p>
          <p className="text-2xl font-bold text-warning">{stats.pendingReview}</p>
        </div>
        <div className="bg-surface/50 rounded-lg border border-gray-800 p-4">
          <p className="text-textSecondary text-sm">Flagged</p>
          <p className="text-2xl font-bold text-orange-500">{stats.flaggedCases}</p>
        </div>
        <div className="bg-surface/50 rounded-lg border border-gray-800 p-4">
          <p className="text-textSecondary text-sm">Fraud Cases</p>
          <p className="text-2xl font-bold text-danger">{stats.fraudCases}</p>
        </div>
        <div className="bg-surface/50 rounded-lg border border-gray-800 p-4">
          <p className="text-textSecondary text-sm">Approved</p>
          <p className="text-2xl font-bold text-success">{stats.approvedCases}</p>
        </div>
      </div>
    </main>
    </div>
  );
}
