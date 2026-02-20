import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Button from '../../components/Button';
import { 
  FiArrowLeft,
  FiSearch,
  FiFilter,
  FiDownload,
  FiRefreshCw,
  FiShield,
  FiAlertTriangle,
  FiCheckCircle,
  FiXCircle,
  FiTrendingUp,
  FiTrendingDown,
  FiEye,
  FiBarChart2,
  FiUsers,
  FiHome,
  FiDollarSign,
  FiClock
} from 'react-icons/fi';

export default function CompanyTrustList() {
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState('all'); // 'all', 'green', 'yellow', 'black'
  const [sortBy, setSortBy] = useState('risk'); // 'risk', 'name', 'claims', 'fraud'

  // Mock data - would come from company_trust_logic.py
  const [companies] = useState([
    {
      id: 'HOSP-001',
      name: 'City General Hospital',
      address: '123 Main St, New York, NY 10001',
      trustScore: 98,
      trustLevel: 'green',
      totalClaims: 450,
      totalAmount: '$2.4M',
      fraudCases: 2,
      fraudRate: '0.5%',
      flaggedClaims: 8,
      approvedClaims: 440,
      avgProcessingTime: '2.3 days',
      riskTrend: 'stable',
      lastIncident: '2024-02-15',
      riskFactors: [
        { name: 'Documentation Quality', score: 95 },
        { name: 'Billing Accuracy', score: 92 },
        { name: 'Claim Pattern', score: 88 }
      ]
    },
    {
      id: 'HOSP-002',
      name: 'MediCare Plus Clinic',
      address: '456 Oak Ave, Los Angeles, CA 90001',
      trustScore: 85,
      trustLevel: 'green',
      totalClaims: 320,
      totalAmount: '$1.8M',
      fraudCases: 3,
      fraudRate: '0.9%',
      flaggedClaims: 12,
      approvedClaims: 305,
      avgProcessingTime: '2.8 days',
      riskTrend: 'stable',
      lastIncident: '2024-02-10',
      riskFactors: [
        { name: 'Documentation Quality', score: 82 },
        { name: 'Billing Accuracy', score: 88 },
        { name: 'Claim Pattern', score: 85 }
      ]
    },
    {
      id: 'HOSP-003',
      name: 'HealthFirst Medical Center',
      address: '789 Pine St, Chicago, IL 60601',
      trustScore: 72,
      trustLevel: 'yellow',
      totalClaims: 280,
      totalAmount: '$1.2M',
      fraudCases: 5,
      fraudRate: '1.8%',
      flaggedClaims: 18,
      approvedClaims: 257,
      avgProcessingTime: '3.2 days',
      riskTrend: 'increasing',
      lastIncident: '2024-02-18',
      riskFactors: [
        { name: 'Documentation Quality', score: 68 },
        { name: 'Billing Accuracy', score: 72 },
        { name: 'Claim Pattern', score: 76 }
      ]
    },
    {
      id: 'HOSP-004',
      name: 'QuickCare Emergency',
      address: '321 Elm St, Houston, TX 77001',
      trustScore: 68,
      trustLevel: 'yellow',
      totalClaims: 195,
      totalAmount: '$890K',
      fraudCases: 4,
      fraudRate: '2.1%',
      flaggedClaims: 15,
      approvedClaims: 176,
      avgProcessingTime: '3.5 days',
      riskTrend: 'increasing',
      lastIncident: '2024-02-20',
      riskFactors: [
        { name: 'Documentation Quality', score: 62 },
        { name: 'Billing Accuracy', score: 70 },
        { name: 'Claim Pattern', score: 72 }
      ]
    },
    {
      id: 'HOSP-005',
      name: 'Premier Health Group',
      address: '555 Cedar Rd, Miami, FL 33101',
      trustScore: 92,
      trustLevel: 'green',
      totalClaims: 520,
      totalAmount: '$3.1M',
      fraudCases: 4,
      fraudRate: '0.8%',
      flaggedClaims: 14,
      approvedClaims: 502,
      avgProcessingTime: '2.1 days',
      riskTrend: 'decreasing',
      lastIncident: '2024-01-25',
      riskFactors: [
        { name: 'Documentation Quality', score: 94 },
        { name: 'Billing Accuracy', score: 90 },
        { name: 'Claim Pattern', score: 92 }
      ]
    },
    {
      id: 'HOSP-006',
      name: 'Community Health Systems',
      address: '777 Birch Ln, Phoenix, AZ 85001',
      trustScore: 45,
      trustLevel: 'black',
      totalClaims: 120,
      totalAmount: '$650K',
      fraudCases: 12,
      fraudRate: '10%',
      flaggedClaims: 28,
      approvedClaims: 80,
      avgProcessingTime: '5.2 days',
      riskTrend: 'increasing',
      lastIncident: '2024-02-22',
      riskFactors: [
        { name: 'Documentation Quality', score: 38 },
        { name: 'Billing Accuracy', score: 42 },
        { name: 'Claim Pattern', score: 45 }
      ]
    },
    {
      id: 'HOSP-007',
      name: 'Sunrise Medical Center',
      address: '888 Spruce Ave, Dallas, TX 75201',
      trustScore: 38,
      trustLevel: 'black',
      totalClaims: 85,
      totalAmount: '$420K',
      fraudCases: 15,
      fraudRate: '17.6%',
      flaggedClaims: 22,
      approvedClaims: 48,
      avgProcessingTime: '6.1 days',
      riskTrend: 'increasing',
      lastIncident: '2024-02-21',
      riskFactors: [
        { name: 'Documentation Quality', score: 32 },
        { name: 'Billing Accuracy', score: 35 },
        { name: 'Claim Pattern', score: 40 }
      ]
    },
    {
      id: 'HOSP-008',
      name: 'Valley Regional Hospital',
      address: '444 Maple Dr, Denver, CO 80201',
      trustScore: 82,
      trustLevel: 'green',
      totalClaims: 380,
      totalAmount: '$2.1M',
      fraudCases: 3,
      fraudRate: '0.8%',
      flaggedClaims: 10,
      approvedClaims: 367,
      avgProcessingTime: '2.5 days',
      riskTrend: 'stable',
      lastIncident: '2024-02-05',
      riskFactors: [
        { name: 'Documentation Quality', score: 84 },
        { name: 'Billing Accuracy', score: 80 },
        { name: 'Claim Pattern', score: 82 }
      ]
    },
    {
      id: 'HOSP-009',
      name: 'Metropolitan Health',
      address: '222 Walnut St, Boston, MA 02101',
      trustScore: 58,
      trustLevel: 'yellow',
      totalClaims: 210,
      totalAmount: '$980K',
      fraudCases: 8,
      fraudRate: '3.8%',
      flaggedClaims: 20,
      approvedClaims: 182,
      avgProcessingTime: '4.0 days',
      riskTrend: 'increasing',
      lastIncident: '2024-02-19',
      riskFactors: [
        { name: 'Documentation Quality', score: 52 },
        { name: 'Billing Accuracy', score: 58 },
        { name: 'Claim Pattern', score: 60 }
      ]
    },
    {
      id: 'HOSP-010',
      name: 'Riverside Medical',
      address: '666 Chestnut Ave, Seattle, WA 98101',
      trustScore: 65,
      trustLevel: 'yellow',
      totalClaims: 175,
      totalAmount: '$820K',
      fraudCases: 6,
      fraudRate: '3.4%',
      flaggedClaims: 16,
      approvedClaims: 153,
      avgProcessingTime: '3.8 days',
      riskTrend: 'stable',
      lastIncident: '2024-02-12',
      riskFactors: [
        { name: 'Documentation Quality', score: 62 },
        { name: 'Billing Accuracy', score: 66 },
        { name: 'Claim Pattern', score: 68 }
      ]
    }
  ]);

  // Stats
  const [stats, setStats] = useState({
    totalCompanies: 0,
    greenList: 0,
    yellowList: 0,
    blackList: 0,
    avgTrustScore: 0,
    totalFraudCases: 0,
    avgFraudRate: 0
  });

  useEffect(() => {
    setTimeout(() => {
      setLoading(false);
      
      // Calculate stats
      const green = companies.filter(c => c.trustLevel === 'green').length;
      const yellow = companies.filter(c => c.trustLevel === 'yellow').length;
      const black = companies.filter(c => c.trustLevel === 'black').length;
      const avgScore = Math.round(companies.reduce((sum, c) => sum + c.trustScore, 0) / companies.length);
      const totalFraud = companies.reduce((sum, c) => sum + c.fraudCases, 0);
      const avgFraud = (companies.reduce((sum, c) => sum + parseFloat(c.fraudRate), 0) / companies.length).toFixed(1);
      
      setStats({
        totalCompanies: companies.length,
        greenList: green,
        yellowList: yellow,
        blackList: black,
        avgTrustScore: avgScore,
        totalFraudCases: totalFraud,
        avgFraudRate: avgFraud
      });
    }, 1000);
  }, []);

  // Filter and search
  const filteredCompanies = companies.filter(company => {
    const matchesSearch = company.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         company.id.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesCategory = filterCategory === 'all' || company.trustLevel === filterCategory;
    
    return matchesSearch && matchesCategory;
  });

  // Sort companies
  const sortedCompanies = [...filteredCompanies].sort((a, b) => {
    if (sortBy === 'name') {
      return a.name.localeCompare(b.name);
    } else if (sortBy === 'claims') {
      return b.totalClaims - a.totalClaims;
    } else if (sortBy === 'fraud') {
      return parseFloat(b.fraudRate) - parseFloat(a.fraudRate);
    } else {
      return b.trustScore - a.trustScore; // risk score
    }
  });

  const getTrustLevelBadge = (level) => {
    switch(level) {
      case 'green':
        return <span className="bg-success/20 text-success px-3 py-1 rounded-full text-sm font-medium">Green List</span>;
      case 'yellow':
        return <span className="bg-warning/20 text-warning px-3 py-1 rounded-full text-sm font-medium">Yellow List</span>;
      case 'black':
        return <span className="bg-danger/20 text-danger px-3 py-1 rounded-full text-sm font-medium">Black List</span>;
      default:
        return null;
    }
  };

  const getTrustColor = (score) => {
    if (score >= 80) return 'text-success';
    if (score >= 60) return 'text-warning';
    return 'text-danger';
  };

  const getTrendIcon = (trend) => {
    if (trend === 'increasing') return <FiTrendingUp className="text-danger" />;
    if (trend === 'decreasing') return <FiTrendingDown className="text-success" />;
    return null;
  };

  const exportToCSV = () => {
    const headers = ['Company ID', 'Company Name', 'Trust Score', 'Trust Level', 'Total Claims', 'Total Amount', 'Fraud Cases', 'Fraud Rate', 'Flagged Claims', 'Avg Processing Time'];
    const csvData = companies.map(c => [
      c.id,
      c.name,
      c.trustScore,
      c.trustLevel,
      c.totalClaims,
      c.totalAmount,
      c.fraudCases,
      c.fraudRate,
      c.flaggedClaims,
      c.avgProcessingTime
    ]);
    
    const csv = [headers, ...csvData].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `company-trust-list-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-textSecondary">Loading company trust data...</p>
        </div>
      </div>
    );
  }

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
            <h1 className="text-xl font-bold">Company Trust List</h1>
            <span className="text-sm bg-primary/20 text-primary px-3 py-1 rounded-full">
              {stats.totalCompanies} Companies
            </span>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-3">
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

      {/* Summary Stats */}
      <div className="px-6 pt-6">
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
          <div className="bg-surface/50 rounded-lg border border-gray-800 p-4">
            <p className="text-textSecondary text-sm">Total Companies</p>
            <p className="text-2xl font-bold">{stats.totalCompanies}</p>
          </div>
          <div className="bg-surface/50 rounded-lg border border-gray-800 p-4">
            <p className="text-textSecondary text-sm">Green List</p>
            <p className="text-2xl font-bold text-success">{stats.greenList}</p>
          </div>
          <div className="bg-surface/50 rounded-lg border border-gray-800 p-4">
            <p className="text-textSecondary text-sm">Yellow List</p>
            <p className="text-2xl font-bold text-warning">{stats.yellowList}</p>
          </div>
          <div className="bg-surface/50 rounded-lg border border-gray-800 p-4">
            <p className="text-textSecondary text-sm">Black List</p>
            <p className="text-2xl font-bold text-danger">{stats.blackList}</p>
          </div>
          <div className="bg-surface/50 rounded-lg border border-gray-800 p-4">
            <p className="text-textSecondary text-sm">Avg Trust Score</p>
            <p className="text-2xl font-bold text-primary">{stats.avgTrustScore}</p>
          </div>
          <div className="bg-surface/50 rounded-lg border border-gray-800 p-4">
            <p className="text-textSecondary text-sm">Avg Fraud Rate</p>
            <p className="text-2xl font-bold text-warning">{stats.avgFraudRate}%</p>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="px-6 pt-6">
        <div className="bg-surface rounded-xl border border-gray-800 p-4">
          <div className="flex items-center gap-6">
            <span className="text-sm font-medium">Trust Level Legend:</span>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-success"></div>
              <span className="text-sm text-textSecondary">Green List (Trusted - Score 80+)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-warning"></div>
              <span className="text-sm text-textSecondary">Yellow List (Monitor - Score 60-79)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-danger"></div>
              <span className="text-sm text-textSecondary">Black List (High Risk - Score &lt;60)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="px-6 pt-6">
        <div className="bg-surface rounded-xl border border-gray-800 p-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <FiSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-textSecondary" />
              <input
                type="text"
                placeholder="Search by company name or ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-background border border-gray-800 rounded-lg py-2 pl-10 pr-4 focus:outline-none focus:border-primary"
              />
            </div>

            {/* Category Filter */}
            <div>
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="w-full bg-background border border-gray-800 rounded-lg py-2 px-3 focus:outline-none focus:border-primary"
              >
                <option value="all">All Trust Levels</option>
                <option value="green">Green List Only</option>
                <option value="yellow">Yellow List Only</option>
                <option value="black">Black List Only</option>
              </select>
            </div>

            {/* Sort By */}
            <div>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full bg-background border border-gray-800 rounded-lg py-2 px-3 focus:outline-none focus:border-primary"
              >
                <option value="risk">Sort by Trust Score</option>
                <option value="name">Sort by Name</option>
                <option value="claims">Sort by Claims</option>
                <option value="fraud">Sort by Fraud Rate</option>
              </select>
            </div>

            {/* Results Count */}
            <div className="flex items-center justify-end">
              <p className="text-sm text-textSecondary">
                Showing {filteredCompanies.length} of {companies.length} companies
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content - Company Cards */}
      <main className="p-6">
        <div className="space-y-4">
          {sortedCompanies.map((company) => (
            <div 
              key={company.id}
              className={`bg-surface rounded-xl border-l-4 p-6 ${
                company.trustLevel === 'green' ? 'border-l-success' :
                company.trustLevel === 'yellow' ? 'border-l-warning' : 'border-l-danger'
              } border-gray-800`}
            >
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                {/* Company Info */}
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <FiHome className="text-primary" />
                    <h2 className="text-xl font-bold">{company.name}</h2>
                    {getTrustLevelBadge(company.trustLevel)}
                  </div>
                  <p className="text-textSecondary text-sm mb-2">{company.address}</p>
                  <p className="text-xs text-textSecondary">ID: {company.id}</p>
                </div>

                {/* Trust Score */}
                <div className="text-center px-4">
                  <p className="text-textSecondary text-sm mb-1">Trust Score</p>
                  <p className={`text-3xl font-bold font-mono ${getTrustColor(company.trustScore)}`}>
                    {company.trustScore}
                  </p>
                  <div className="flex items-center gap-1 mt-1">
                    {getTrendIcon(company.riskTrend)}
                    <span className="text-xs text-textSecondary">{company.riskTrend}</span>
                  </div>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 flex-1">
                  <div>
                    <p className="text-textSecondary text-xs">Total Claims</p>
                    <p className="text-lg font-bold">{company.totalClaims}</p>
                    <p className="text-xs text-textSecondary">{company.totalAmount}</p>
                  </div>
                  <div>
                    <p className="text-textSecondary text-xs">Fraud Cases</p>
                    <p className="text-lg font-bold text-danger">{company.fraudCases}</p>
                    <p className="text-xs text-textSecondary">{company.fraudRate} rate</p>
                  </div>
                  <div>
                    <p className="text-textSecondary text-xs">Flagged</p>
                    <p className="text-lg font-bold text-warning">{company.flaggedClaims}</p>
                  </div>
                  <div>
                    <p className="text-textSecondary text-xs">Approved</p>
                    <p className="text-lg font-bold text-success">{company.approvedClaims}</p>
                  </div>
                </div>

                {/* Risk Factors */}
                <div className="min-w-[200px]">
                  <p className="text-textSecondary text-xs mb-2">Risk Factors</p>
                  {company.riskFactors.map((factor, idx) => (
                    <div key={idx} className="mb-2">
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-textSecondary">{factor.name}</span>
                        <span className={factor.score >= 80 ? 'text-success' : factor.score >= 60 ? 'text-warning' : 'text-danger'}>
                          {factor.score}
                        </span>
                      </div>
                      <div className="w-full bg-background rounded-full h-1">
                        <div 
                          className={`h-1 rounded-full ${
                            factor.score >= 80 ? 'bg-success' : 
                            factor.score >= 60 ? 'bg-warning' : 'bg-danger'
                          }`}
                          style={{ width: `${factor.score}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Actions */}
                <div>
                  <Link to={`/insurance/companies/${company.id}`}>
                    <Button variant="secondary" size="sm" className="flex items-center gap-2">
                      <FiEye />
                      View Details
                    </Button>
                  </Link>
                </div>
              </div>

              {/* Footer Stats */}
              <div className="mt-4 pt-4 border-t border-gray-800 flex flex-wrap gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <FiClock className="text-textSecondary" />
                  <span className="text-textSecondary">Avg Processing:</span>
                  <span>{company.avgProcessingTime}</span>
                </div>
                <div className="flex items-center gap-2">
                  <FiAlertTriangle className="text-textSecondary" />
                  <span className="text-textSecondary">Last Incident:</span>
                  <span>{company.lastIncident}</span>
                </div>
              </div>
            </div>
          ))}

          {/* Empty State */}
          {filteredCompanies.length === 0 && (
            <div className="bg-surface rounded-xl border border-gray-800 p-12 text-center">
              <FiShield className="text-4xl text-textSecondary mx-auto mb-4" />
              <h3 className="text-lg font-bold mb-2">No companies found</h3>
              <p className="text-textSecondary mb-4">Try adjusting your search or filters</p>
              <Button onClick={() => {
                setSearchTerm('');
                setFilterCategory('all');
                setSortBy('risk');
              }}>
                Clear Filters
              </Button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
