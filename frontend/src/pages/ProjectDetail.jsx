import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { projects, tasks } from '../api/client';

export default function ProjectDetail() {
  const { id } = useParams();
  const [project, setProject] = useState(null);
  const [title, setTitle] = useState('');
  const [err, setErr] = useState(null);

  const load = () => projects.get(id).then(setProject).catch((e) => setErr(e.message));
  useEffect(() => { load(); }, [id]);

  const addTask = async (e) => {
    e.preventDefault();
    setErr(null);
    try {
      await tasks.create({ title, project_id: Number(id) });
      setTitle('');
      load();
    } catch (e2) {
      setErr(e2.message);
    }
  };

  const cycle = async (t) => {
    const next = { todo: 'in_progress', in_progress: 'done', done: 'todo' }[t.status];
    await tasks.update(t.id, { status: next });
    load();
  };

  if (!project) return <p className="muted">{err || 'Cargando…'}</p>;

  return (
    <div className="stack">
      <p><Link to="/projects">← Proyectos</Link></p>
      <h1>{project.title}</h1>
      <p className="muted">{project.status} · {project.tech_stack || 'sin stack'}</p>

      <form className="row" onSubmit={addTask}>
        <input placeholder="Nueva tarea" value={title}
          onChange={(e) => setTitle(e.target.value)} required />
        <button>Añadir tarea</button>
      </form>
      {err && <p className="error">{err}</p>}

      <ul className="tasks">
        {project.tasks.map((t) => (
          <li key={t.id}>
            <button className={`chip ${t.status}`} onClick={() => cycle(t)}>{t.status}</button>
            <span>{t.title}</span>
            <button className="link" onClick={() => tasks.remove(t.id).then(load)}>x</button>
          </li>
        ))}
        {project.tasks.length === 0 && <li className="muted">Sin tareas.</li>}
      </ul>
    </div>
  );
}
