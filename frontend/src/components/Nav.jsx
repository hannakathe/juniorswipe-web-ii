import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Nav() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  if (!user) return null;

  const doLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="nav">
      <span className="brand">JuniorSwipe</span>
      <nav>
        <NavLink to="/">Panel</NavLink>
        <NavLink to="/projects">Proyectos</NavLink>
        <NavLink to="/profile">Perfil</NavLink>
        {user.role === 'developer' && <NavLink to="/resumes">CV</NavLink>}
      </nav>
      <div className="nav-right">
        <span className="muted">{user.email} · {user.role}</span>
        <button onClick={doLogout}>Salir</button>
      </div>
    </header>
  );
}
