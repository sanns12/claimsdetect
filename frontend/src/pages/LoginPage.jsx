import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Button from '../components/Button';
import { FiMail, FiLock, FiUser, FiArrowRight } from 'react-icons/fi';
import { USER_ROLES } from '../utils/constants';

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState(USER_ROLES.USER);
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Simulate login validation
    setTimeout(() => {
      // Basic validation
      if (!email || !password) {
        setError('Please fill in all fields');
        setLoading(false);
        return;
      }

      // For demo purposes, accept any email/password
      // In real app, you'd call an API here
      console.log('Login successful', { email, password, role, rememberMe });
      
      // Store user info based on role
      const userData = {
        email,
        role,
        name: email.split('@')[0], // Simple name from email
      };
      
      // Save to localStorage if remember me is checked
      if (rememberMe) {
        localStorage.setItem('user', JSON.stringify(userData));
      } else {
        sessionStorage.setItem('user', JSON.stringify(userData));
      }

      // Redirect based on role
      setLoading(false);
      
      switch(role) {
        case USER_ROLES.USER:
          navigate('/user/dashboard');
          break;
        case USER_ROLES.HOSPITAL:
          navigate('/hospital/dashboard');
          break;
        case USER_ROLES.INSURANCE:
          navigate('/insurance/dashboard');
          break;
        default:
          navigate('/user/dashboard');
      }
    }, 1000); // Simulate API delay
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

          {/* Error Message */}
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

          {/* Demo credentials hint */}
          <div className="mt-8 p-4 bg-surface/50 rounded-lg border border-gray-800">
            <p className="text-sm text-textSecondary mb-2">Demo Credentials:</p>
            <p className="text-xs text-textSecondary">Any email/password works</p>
            <p className="text-xs text-textSecondary mt-1">Try: user@example.com / any password</p>
          </div>
        </div>
      </div>

      {/* Right Panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary/10 to-transparent items-center justify-center p-8">
        <div className="text-center">
          <p className="text-3xl font-bold mb-4">Secure • AI-Powered • Real-time</p>
          <p className="text-textSecondary">Advanced fraud detection at scale</p>
        </div>
      </div>
    </div>
  );
}