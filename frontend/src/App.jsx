import { BrowserRouter, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import RouteGuard from "./components/RouteGuard";
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
        <Route path="/user/dashboard" element={
          <RouteGuard allowedRoles={['User']}>
            <UserDashboard />
          </RouteGuard>
        } />
        <Route path="/user/submit-claim" element={
          <RouteGuard allowedRoles={['User']}>
            <UserSubmitClaim />
          </RouteGuard>
        } />
        <Route path="/user/claims" element={
          <RouteGuard allowedRoles={['User']}>
            <UserClaimList />
          </RouteGuard>
        } />
        <Route path="/user/claims/:id" element={
          <RouteGuard allowedRoles={['User']}>
            <UserClaimDetail />
          </RouteGuard>
        } />
        
        {/* Hospital Routes */}
        <Route path="/hospital/dashboard" element={
          <RouteGuard allowedRoles={['Hospital']}>
            <HospitalDashboard />
          </RouteGuard>
        } />
        <Route path="/hospital/submit-claim" element={
          <RouteGuard allowedRoles={['Hospital']}>
            <HospitalSubmitClaim />
          </RouteGuard>
        } />
        <Route path="/hospital/claims" element={
          <RouteGuard allowedRoles={['Hospital']}>
            <HospitalClaimsList />
          </RouteGuard>
        } />
        <Route path="/hospital/claims/:id" element={
          <RouteGuard allowedRoles={['Hospital']}>
            <HospitalClaimDetail />
          </RouteGuard>
        } />
        
        {/* Insurance Routes */}
        <Route path="/insurance/dashboard" element={
          <RouteGuard allowedRoles={['Insurance']}>
            <InsuranceDashboard />
          </RouteGuard>
        } />
        <Route path="/insurance/claims" element={
          <RouteGuard allowedRoles={['Insurance']}>
            <InsuranceClaimsList />
          </RouteGuard>
        } />
        <Route path="/insurance/claims/:id" element={
          <RouteGuard allowedRoles={['Insurance']}>
            <InsuranceClaimDetail />
          </RouteGuard>
        } />
        <Route path="/insurance/companies" element={
          <RouteGuard allowedRoles={['Insurance']}>
            <CompanyTrustList />
          </RouteGuard>
        } />
      </Routes>
    </BrowserRouter>
  );
}

export default App;