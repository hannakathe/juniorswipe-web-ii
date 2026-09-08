import { useEffect, useState } from 'react';
import { profile } from '../api/client';

export default function Profile() {
  const [form, setForm] = useState(null);
  const [msg, setMsg] = useState(null);
  const [err, setErr] = useState(null);

  useEffect(() => {
    profile.get().then((p) => setForm({
      headline: p.headline || '', bio: p.bio || '', location: p.location || '',
      website: p.website || '', company_name: p.company_name || '',
      skills: (p.skills || []).join(', '),
    })).catch((e) => setErr(e.message));
  }, []);

  if (!form) return <p className="muted">{err || 'Cargando…'}</p>;

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const save = async (e) => {
    e.preventDefault();
    setMsg(null); setErr(null);
    try {
      const payload = {
        ...form,
        skills: form.skills.split(',').map((s) => s.trim()).filter(Boolean),
      };
      await profile.update(payload);
      setMsg('Perfil guardado');
    } catch (e2) {
      setErr(e2.message);
    }
  };

  return (
    <form className="card stack" onSubmit={save}>
      <h1>Mi perfil</h1>
      <label>Titular<input value={form.headline} onChange={set('headline')} /></label>
      <label>Bio<textarea value={form.bio} onChange={set('bio')} rows={3} /></label>
      <label>Ubicación<input value={form.location} onChange={set('location')} /></label>
      <label>Sitio web<input value={form.website} onChange={set('website')} /></label>
      <label>Empresa<input value={form.company_name} onChange={set('company_name')} /></label>
      <label>Habilidades (separadas por coma)
        <input value={form.skills} onChange={set('skills')} /></label>
      {msg && <p className="ok">{msg}</p>}
      {err && <p className="error">{err}</p>}
      <button>Guardar</button>
    </form>
  );
}
