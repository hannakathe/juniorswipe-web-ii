import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [err, setErr] = useState(null);

  useEffect(() => {
    api.get('/api/users/me').then(setStats).catch((e) => setErr(e.message));
  }, []);

  return (
    <div className="stack">
      <h1>Hola, {user.full_name}</h1>
      {err && <p className="error">{err}</p>}
      {stats && (
        <div className="grid">
          <div className="card"><h3>{stats.project_count}</h3><p className="muted">Proyectos</p>
            <Link to="/projects">Ver</Link></div>
          <div className="card"><h3>{stats.resume_count}</h3><p className="muted">CVs</p>
            {user.role === 'developer' && <Link to="/resumes">Ver</Link>}</div>
          <div className="card"><h3>{stats.role}</h3><p className="muted">Rol</p>
            <Link to="/profile">Perfil</Link></div>
        </div>
      )}
    </div>
  );
}
