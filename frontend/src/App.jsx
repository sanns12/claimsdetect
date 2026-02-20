import { BrowserRouter, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import UserDashboard from "./pages/user/UserDashboard";
import UserSubmitClaim from "./pages/user/UserSubmitClaim";
import UserClaimList from "./pages/user/UserClaimList";
import UserClaimDetail from "./pages/user/UserClaimDetail";
import HospitalDashboard from "./pages/hospital/HospitalDashboard";
import HospitalSubmitClaim from "./pages/hospital/HospitalSubmitClaim";
import HospitalClaimsList from "./pages/hospital/HospitalClaimsList";
import HospitalClaimDetail from "./pages/hospital/HospitalClaimDetail";
import InsuranceDashboard from "./pages/insurance/InsuranceDashboard";
import InsuranceClaimsList from "./pages/insurance/InsuranceClaimList";
import InsuranceClaimDetail from "./pages/insurance/InsuranceClaimDetail";
import CompanyTrustList from "./pages/insurance/CompanyTrustList";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        
        {/* User Routes */}
        <Route path="/user/dashboard" element={<UserDashboard />} />
        <Route path="/user/submit-claim" element={<UserSubmitClaim />} />
        <Route path="/user/claims" element={<UserClaimList />} />
        <Route path="/user/claims/:id" element={<UserClaimDetail />} />
        
        {/* Hospital Routes */}
        <Route path="/hospital/dashboard" element={<HospitalDashboard />} />
        <Route path="/hospital/submit-claim" element={<HospitalSubmitClaim />} />
        <Route path="/hospital/claims" element={<HospitalClaimsList />} />
        <Route path="/hospital/claims/:id" element={<HospitalClaimDetail />} />
        
        {/* Insurance Routes */}
        <Route path="/insurance/dashboard" element={<InsuranceDashboard />} />
        <Route path="/insurance/claims" element={<InsuranceClaimsList />} />
        <Route path="/insurance/claims/:id" element={<InsuranceClaimDetail />} />
        <Route path="/insurance/companies" element={<CompanyTrustList />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;