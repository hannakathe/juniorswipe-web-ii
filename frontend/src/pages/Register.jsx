import { useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Register() {
  const { user, register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    full_name: '', email: '', password: '', role: 'developer',
  });
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to="/" replace />;

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await register(form);
      navigate('/');
    } catch (err) {
      setError(err.message || 'No se pudo registrar');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth-wrap">
      <form className="card" onSubmit={submit}>
        <h1>Crear cuenta</h1>
        <label>Nombre completo
          <input value={form.full_name} onChange={set('full_name')} required minLength={3} />
        </label>
        <label>Correo
          <input type="email" value={form.email} onChange={set('email')} required />
        </label>
        <label>Contraseña
          <input type="password" value={form.password} onChange={set('password')}
            required minLength={8} />
        </label>
        <label>Tipo de cuenta
          <select value={form.role} onChange={set('role')}>
            <option value="developer">Desarrollador</option>
            <option value="company">Empresa</option>
          </select>
        </label>
        {error && <p className="error" role="alert">{error}</p>}
        <button disabled={busy}>{busy ? 'Creando…' : 'Registrarme'}</button>
        <p className="muted">¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link></p>
      </form>
    </div>
  );
}
