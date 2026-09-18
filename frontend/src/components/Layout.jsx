import { Link, useNavigate } from 'react-router-dom';
import { clearSession, getUser } from '../api';

export default function Layout({ children }) {
  const navigate = useNavigate();
  const user = getUser();

  function logout() {
    clearSession();
    navigate('/login');
  }

  return (
    <>
      <div className="topbar">
        <h1>
          <Link to="/" style={{ textDecoration: 'none' }}>
            Darukaa.Earth
          </Link>
        </h1>
        <div>
          <span className="muted" style={{ marginRight: 14 }}>
            {user?.full_name}
          </span>
          <button className="ghost" onClick={logout}>
            Log out
          </button>
        </div>
      </div>
      <div className="page">{children}</div>
    </>
  );
}
