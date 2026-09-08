import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { projects } from '../api/client';

export default function Projects() {
  const [items, setItems] = useState([]);
  const [title, setTitle] = useState('');
  const [status, setStatus] = useState('draft');
  const [err, setErr] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    projects.list('?per_page=50')
      .then((r) => setItems(r.items))
      .catch((e) => setErr(e.message))
      .finally(() => setLoading(false));
  };
  useEffect(load, []);

  const create = async (e) => {
    e.preventDefault();
    setErr(null);
    try {
      await projects.create({ title, status });
      setTitle('');
      load();
    } catch (e2) {
      setErr(e2.message);
    }
  };

  const remove = async (id) => {
    await projects.remove(id);
    load();
  };

  return (
    <div className="stack">
      <h1>Proyectos</h1>
      <form className="row" onSubmit={create}>
        <input placeholder="Título del proyecto" value={title}
          onChange={(e) => setTitle(e.target.value)} required />
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          {['draft', 'open', 'active', 'closed'].map((s) => <option key={s}>{s}</option>)}
        </select>
        <button>Crear</button>
      </form>
      {err && <p className="error">{err}</p>}
      {loading ? <p className="muted">Cargando…</p> : (
        <table className="table">
          <thead><tr><th>Título</th><th>Estado</th><th>Tareas</th><th /></tr></thead>
          <tbody>
            {items.map((p) => (
              <tr key={p.id}>
                <td><Link to={`/projects/${p.id}`}>{p.title}</Link></td>
                <td>{p.status}</td>
                <td>{p.task_count}</td>
                <td><button className="link" onClick={() => remove(p.id)}>Eliminar</button></td>
              </tr>
            ))}
            {items.length === 0 && <tr><td colSpan={4} className="muted">Sin proyectos aún.</td></tr>}
          </tbody>
        </table>
      )}
    </div>
  );
}
