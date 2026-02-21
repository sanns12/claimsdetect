import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Button from '../components/Button';
import { FiMail, FiLock, FiUser, FiArrowRight } from 'react-icons/fi';
import { USER_ROLES } from '../utils/constants';
import { login } from '../services/auth';

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState(USER_ROLES.USER);
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Prevent multiple submissions
    if (loading) return;
    
    setError('');
    setLoading(true);

    try {
      console.log('Attempting login with:', { email, role });
      
      const response = await login(email, password, role);
      
      console.log('Login response:', response);
      
      if (response.token) {
        // Store token and user data
        localStorage.setItem('token', response.token);
        localStorage.setItem('user', JSON.stringify(response.user));
        localStorage.setItem('role', role);
        
        // Redirect based on role
        const redirectPath = role === USER_ROLES.USER ? '/user/dashboard' :
                            role === USER_ROLES.HOSPITAL ? '/hospital/dashboard' :
                            '/insurance/dashboard';
        
        console.log('Redirecting to:', redirectPath);
        navigate(redirectPath, { replace: true });
      }
    } catch (err) {
      console.error('Login error:', err);
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-white flex">
      {/* Left Panel - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="max-w-md w-full">
          <Link to="/" className="text-2xl font-bold text-primary mb-8 inline-block">
            InsureVerify
          </Link>
          <h2 className="text-3xl font-bold mb-2">Welcome Back</h2>
          <p className="text-textSecondary mb-8">Sign in to your account</p>

          {error && (
            <div className="bg-danger/10 border border-danger/30 text-danger px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium mb-2">Email</label>
              <div className="relative">
                <FiMail className="absolute left-3 top-1/2 -translate-y-1/2 text-textSecondary" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-surface border border-gray-800 rounded-lg py-3 pl-10 pr-4 focus:outline-none focus:border-primary transition-colors"
                  placeholder="Enter your email"
                  required
                  disabled={loading}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Password</label>
              <div className="relative">
                <FiLock className="absolute left-3 top-1/2 -translate-y-1/2 text-textSecondary" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-surface border border-gray-800 rounded-lg py-3 pl-10 pr-4 focus:outline-none focus:border-primary transition-colors"
                  placeholder="Enter your password"
                  required
                  disabled={loading}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Login as</label>
              <div className="relative">
                <FiUser className="absolute left-3 top-1/2 -translate-y-1/2 text-textSecondary z-10" />
                <select
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className="w-full bg-surface border border-gray-800 rounded-lg py-3 pl-10 pr-4 appearance-none focus:outline-none focus:border-primary transition-colors"
                  disabled={loading}
                >
                  {Object.values(USER_ROLES).map((r) => (
                    <option key={r} value={r}>{r}</option>
                  ))}
                </select>
                <FiArrowRight className="absolute right-3 top-1/2 -translate-y-1/2 text-textSecondary rotate-90" />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 rounded border-gray-800 bg-surface text-primary focus:ring-primary"
                  disabled={loading}
                />
                <span className="text-sm text-textSecondary">Remember me</span>
              </label>
              <Link to="/forgot-password" className="text-sm text-primary hover:underline">
                Forgot password?
              </Link>
            </div>

            <Button 
              type="submit" 
              className="w-full"
              disabled={loading}
            >
              {loading ? 'Logging in...' : 'Login'}
            </Button>

            <p className="text-center text-textSecondary">
              Don't have an account?{' '}
              <Link to="/signup" className="text-primary hover:underline">
                Sign up
              </Link>
            </p>
          </form>

          <div className="mt-8 p-4 bg-surface/50 rounded-lg border border-gray-800">
            <p className="text-sm text-textSecondary mb-2">Demo Credentials:</p>
            <p className="text-xs text-textSecondary">Email: user@example.com</p>
            <p className="text-xs text-textSecondary">Password: password123</p>
            <p className="text-xs text-textSecondary mt-1">Any role works</p>
          </div>
        </div>
      </div>

      {/* Right Panel - Neural Network Visualization */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary/5 to-transparent items-center justify-center p-8 relative overflow-hidden">
        {/* ... your existing neural network visualization ... */}
        <div className="absolute bottom-12 left-12 text-white z-10">
          <p className="text-2xl font-bold mb-2 bg-gradient-to-r from-primary to-white bg-clip-text text-transparent">
            Secure • AI-Powered • Real-time
          </p>
          <p className="text-textSecondary">Advanced fraud detection at scale</p>
        </div>
      </div>
    </div>
  );
}