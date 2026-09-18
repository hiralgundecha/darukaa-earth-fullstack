import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';
import Layout from '../components/Layout';

export default function Dashboard() {
  const [projects, setProjects] = useState([]);
  const [form, setForm] = useState({ name: '', description: '', project_type: 'carbon' });
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .listProjects()
      .then(setProjects)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  async function createProject(e) {
    e.preventDefault();
    try {
      const created = await api.createProject(form);
      setProjects([created, ...projects]);
      setForm({ name: '', description: '', project_type: 'carbon' });
      setShowForm(false);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <Layout>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ marginBottom: 2 }}>Projects</h2>
          <p className="muted">Each project holds one or more mapped sites.</p>
        </div>
        <button onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'New project'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {showForm && (
        <form className="card" onSubmit={createProject}>
          <label>Project name</label>
          <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          <label>Description</label>
          <textarea
            rows="2"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
          <label>Type</label>
          <select
            value={form.project_type}
            onChange={(e) => setForm({ ...form, project_type: e.target.value })}
          >
            <option value="carbon">Carbon</option>
            <option value="biodiversity">Biodiversity</option>
            <option value="mixed">Mixed</option>
          </select>
          <button type="submit">Create project</button>
        </form>
      )}

      {loading && <p className="muted">Loading your projects…</p>}

      {!loading && projects.length === 0 && (
        <div className="card">
          <p className="muted">No projects yet. Create one to start mapping sites.</p>
        </div>
      )}

      <div className="grid">
        {projects.map((p) => (
          <Link key={p.id} to={`/projects/${p.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
            <div className="card">
              <h3>{p.name}</h3>
              <p className="muted">{p.description || 'No description'}</p>
              <p className="muted">
                {p.site_count} site{p.site_count === 1 ? '' : 's'} · {p.project_type}
              </p>
            </div>
          </Link>
        ))}
      </div>
    </Layout>
  );
}
