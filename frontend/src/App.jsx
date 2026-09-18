import { Navigate, Route, Routes } from 'react-router-dom';
import { getToken } from './api';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import ProjectMap from './pages/ProjectMap';
import SiteDetail from './pages/SiteDetail';

function Protected({ children }) {
  return getToken() ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/" element={<Protected><Dashboard /></Protected>} />
      <Route path="/projects/:id" element={<Protected><ProjectMap /></Protected>} />
      <Route path="/sites/:id" element={<Protected><SiteDetail /></Protected>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
