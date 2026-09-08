import { useEffect, useRef, useState } from 'react';
import { api, resumes } from '../api/client';

export default function Resumes() {
  const [items, setItems] = useState([]);
  const [title, setTitle] = useState('');
  const [summary, setSummary] = useState('');
  const [err, setErr] = useState(null);
  const fileRef = useRef(null);

  const load = () => resumes.list().then((r) => setItems(r.items)).catch((e) => setErr(e.message));
  useEffect(() => { load(); }, []);

  const create = async (e) => {
    e.preventDefault();
    setErr(null);
    const fd = new FormData();
    fd.append('title', title);
    fd.append('summary', summary);
    if (fileRef.current?.files[0]) fd.append('file', fileRef.current.files[0]);
    try {
      await resumes.create(fd);
      setTitle(''); setSummary('');
      if (fileRef.current) fileRef.current.value = '';
      load();
    } catch (e2) {
      setErr(e2.message);
    }
  };

  const download = async (r) => {
    const res = await api.raw('GET', `/api/resumes/${r.id}/file`);
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = r.original_filename || 'cv';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="stack">
      <h1>Mis CV</h1>
      <form className="card stack" onSubmit={create}>
        <label>Título<input value={title} onChange={(e) => setTitle(e.target.value)} required /></label>
        <label>Resumen<input value={summary} onChange={(e) => setSummary(e.target.value)} /></label>
        <label>Archivo (PDF/DOC/TXT)<input type="file" ref={fileRef}
          accept=".pdf,.doc,.docx,.txt,.md" /></label>
        <button>Subir CV</button>
      </form>
      {err && <p className="error">{err}</p>}
      <ul className="tasks">
        {items.map((r) => (
          <li key={r.id}>
            <span>{r.is_primary ? '★ ' : ''}{r.title}</span>
            <span className="muted">{r.has_file ? `${r.size_bytes} B` : 'sin archivo'}</span>
            {r.has_file && <button className="link" onClick={() => download(r)}>descargar</button>}
            <button className="link" onClick={() => resumes.remove(r.id).then(load)}>x</button>
          </li>
        ))}
        {items.length === 0 && <li className="muted">Aún no has subido tu CV.</li>}
      </ul>
    </div>
  );
}
