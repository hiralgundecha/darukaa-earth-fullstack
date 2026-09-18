import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { api } from '../api';
import Layout from '../components/Layout';
import MetricChart from '../components/MetricChart';

function change(points) {
  if (points.length < 2) return null;
  const first = points[0].value;
  const last = points[points.length - 1].value;
  const pct = ((last - first) / first) * 100;
  return `${pct >= 0 ? '+' : ''}${pct.toFixed(1)}%`;
}

export default function SiteDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [site, setSite] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api.getSite(id).then(setSite).catch((e) => setError(e.message));
  }, [id]);

  async function remove() {
    if (!window.confirm('Delete this site and its metrics? This cannot be undone.')) return;
    await api.deleteSite(id);
    navigate(`/projects/${site.project_id}`);
  }

  if (error) return <Layout><div className="error">{error}</div></Layout>;
  if (!site) return <Layout><p className="muted">Loading site…</p></Layout>;

  const keys = Object.keys(site.metrics);

  return (
    <Layout>
      <p className="muted">
        <a href={`/projects/${site.project_id}`}>← {site.project_name}</a>
      </p>
      <h2 style={{ marginBottom: 2 }}>{site.name}</h2>
      <p className="muted">
        {site.area_hectares} hectares · {site.land_cover} · centroid{' '}
        {site.centroid[1].toFixed(4)}, {site.centroid[0].toFixed(4)}
      </p>

      <div className="split">
        <div>
          {keys.length === 0 && (
            <div className="card">
              <p className="muted">
                No monitoring data recorded for this site yet. Sites you draw yourself start
                empty; the seeded demo sites have four years of readings.
              </p>
            </div>
          )}
          {keys.map((key) => (
            <MetricChart key={key} metricKey={key} points={site.metrics[key]} />
          ))}
        </div>

        <div>
          <div className="card">
            <h3>Change since baseline</h3>
            {keys.length === 0 && <p className="muted">Nothing to compare yet.</p>}
            {keys.map((key) => (
              <div key={key} className="stat">
                <span>{key.replace(/_/g, ' ')}</span>
                <strong>{change(site.metrics[key]) || '—'}</strong>
              </div>
            ))}
          </div>

          <div className="card">
            <h3>Site record</h3>
            <div className="stat"><span>Area</span><span>{site.area_hectares} ha</span></div>
            <div className="stat"><span>Land cover</span><span>{site.land_cover}</span></div>
            <div className="stat"><span>Added</span><span>{site.created_at.slice(0, 10)}</span></div>
            <button className="ghost" style={{ marginTop: 12 }} onClick={remove}>
              Delete site
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
}
