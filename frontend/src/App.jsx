import { BrowserRouter, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import UserDashboard from "./pages/user/UserDashboard";
import UserSubmitClaim from "./pages/user/UserSubmitClaim";
import UserClaimList from "./pages/user/UserClaimList";
import UserClaimDetail from "./pages/user/UserClaimDetail";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/user/dashboard" element={<UserDashboard />} />
        <Route path="/user/submit-claim" element={<UserSubmitClaim />} />
        <Route path="/user/claims" element={<UserClaimList />} />
        <Route path="/user/claims/:id" element={<UserClaimDetail />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;