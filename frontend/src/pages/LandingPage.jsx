import { Link } from "react-router-dom";
import Button from "../components/Button";
import { FiUser, FiHome, FiShield } from "react-icons/fi";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background text-white">
      {/* Navigation */}
      <nav className="flex justify-between items-center p-6 border-b border-surface">
        <h1 className="text-2xl font-bold text-primary">InsureVerify</h1>
        <Link to="/login">
          <Button variant="secondary">Login</Button>
        </Link>
      </nav>

      {/* Hero Section */}
      <main className="flex flex-col items-center mt-16 px-4">
        <h2 className="text-5xl font-bold text-center max-w-4xl leading-tight">
          AI-Powered Insurance Claim
          <span className="text-primary block">Verification System</span>
        </h2>

        <p className="text-textSecondary text-xl mt-6 text-center max-w-2xl">
          Real-time fraud detection with machine learning
        </p>

        <Link to="/signup">
          <Button size="lg" className="mt-8">
            Get Started
          </Button>
        </Link>

        {/* Role Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-20 max-w-5xl">
          {/* User Card */}
          <div className="bg-surface p-6 rounded-xl border border-gray-800 hover:border-primary transition-all">
            <FiUser className="text-primary text-4xl mb-4" />
            <h3 className="text-xl font-bold mb-2">For Users</h3>
            <ul className="text-textSecondary space-y-2">
              <li className="flex items-center gap-2">
                <span className="text-success">✓</span> Submit claims
              </li>
              <li className="flex items-center gap-2">
                <span className="text-success">✓</span> Track status
              </li>
              <li className="flex items-center gap-2">
                <span className="text-success">✓</span> View history
              </li>
            </ul>
          </div>

          {/* Hospital Card */}
          <div className="bg-surface p-6 rounded-xl border border-gray-800 hover:border-primary transition-all">
            <FiHome className="text-primary text-4xl mb-4" />
            <h3 className="text-xl font-bold mb-2">For Hospitals</h3>
            <ul className="text-textSecondary space-y-2">
              <li className="flex items-center gap-2">
                <span className="text-success">✓</span> Bulk upload
              </li>
              <li className="flex items-center gap-2">
                <span className="text-success">✓</span> Patient verification
              </li>
              <li className="flex items-center gap-2">
                <span className="text-success">✓</span> Department stats
              </li>
            </ul>
          </div>

          {/* Insurance Card */}
          <div className="bg-surface p-6 rounded-xl border border-gray-800 hover:border-primary transition-all">
            <FiShield className="text-primary text-4xl mb-4" />
            <h3 className="text-xl font-bold mb-2">For Insurers</h3>
            <ul className="text-textSecondary space-y-2">
              <li className="flex items-center gap-2">
                <span className="text-success">✓</span> Risk analysis
              </li>
              <li className="flex items-center gap-2">
                <span className="text-success">✓</span> Fraud detection
              </li>
              <li className="flex items-center gap-2">
                <span className="text-success">✓</span> Company trust scores
              </li>
            </ul>
          </div>
        </div>

        {/* Trust Badges */}
        <div className="flex flex-wrap justify-center gap-8 mt-20 text-textSecondary border-t border-surface pt-8 w-full max-w-4xl">
          <span className="flex items-center gap-2">
            <span className="text-success">✓</span> 100K+ Claims Processed
          </span>
          <span className="flex items-center gap-2">
            <span className="text-success">✓</span> 99.9% Accuracy
          </span>
          <span className="flex items-center gap-2">
            <span className="text-success">✓</span> ISO 27001 Certified
          </span>
        </div>
      </main>
    </div>
  );
}
