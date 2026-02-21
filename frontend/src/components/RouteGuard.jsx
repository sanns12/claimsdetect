import { Navigate } from 'react-router-dom';
import { isAuthenticated, getCurrentRole } from '../services/auth';

const RouteGuard = ({ children, allowedRoles = [] }) => {
  const authenticated = isAuthenticated();
  const userRole = getCurrentRole();

  if (!authenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(userRole)) {
    return <Navigate to="/" replace />;
  }

  return children;
};

export default RouteGuard;