import { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import mapboxgl from 'mapbox-gl';
import MapboxDraw from '@mapbox/mapbox-gl-draw';
import 'mapbox-gl/dist/mapbox-gl.css';
import '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css';
import { api } from '../api';
import Layout from '../components/Layout';

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN;

export default function ProjectMap() {
  const { id } = useParams();
  const navigate = useNavigate();
  const container = useRef(null);
  const mapRef = useRef(null);
  const drawRef = useRef(null);

  const [project, setProject] = useState(null);
  const [drawn, setDrawn] = useState(null);
  const [form, setForm] = useState({ name: '', land_cover: 'forest' });
  const [error, setError] = useState('');

  useEffect(() => {
    api.getProject(id).then(setProject).catch((e) => setError(e.message));
  }, [id]);

  useEffect(() => {
    if (!project || mapRef.current) return;

    const first = project.sites[0];
    const map = new mapboxgl.Map({
      container: container.current,
      style: 'mapbox://styles/mapbox/satellite-streets-v12',
      center: first ? first.centroid : [73.11, 18.99],
      zoom: first ? 12 : 10,
    });

    const draw = new MapboxDraw({
      displayControlsDefault: false,
      controls: { polygon: true, trash: true },
    });

    map.addControl(new mapboxgl.NavigationControl(), 'top-right');
    map.addControl(draw, 'top-left');
    mapRef.current = map;
    drawRef.current = draw;

    map.on('load', () => {
      map.addSource('sites', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: project.sites.map((s) => ({
            type: 'Feature',
            geometry: s.geometry,
            properties: { id: s.id, name: s.name, area: s.area_hectares },
          })),
        },
      });
      map.addLayer({
        id: 'sites-fill',
        type: 'fill',
        source: 'sites',
        paint: { 'fill-color': '#1f6f4a', 'fill-opacity': 0.35 },
      });
      map.addLayer({
        id: 'sites-line',
        type: 'line',
        source: 'sites',
        paint: { 'line-color': '#ffffff', 'line-width': 2 },
      });

      map.on('click', 'sites-fill', (e) => {
        navigate(`/sites/${e.features[0].properties.id}`);
      });
      map.on('mouseenter', 'sites-fill', () => (map.getCanvas().style.cursor = 'pointer'));
      map.on('mouseleave', 'sites-fill', () => (map.getCanvas().style.cursor = ''));
    });

    map.on('draw.create', (e) => setDrawn(e.features[0].geometry));
    map.on('draw.update', (e) => setDrawn(e.features[0].geometry));
    map.on('draw.delete', () => setDrawn(null));

    return () => map.remove();
  }, [project, navigate]);

  async function saveSite(e) {
    e.preventDefault();
    setError('');
    try {
      const site = await api.createSite(id, { ...form, geometry: drawn });
      setProject({ ...project, sites: [...project.sites, site] });
      drawRef.current.deleteAll();
      setDrawn(null);
      setForm({ name: '', land_cover: 'forest' });

      mapRef.current.getSource('sites').setData({
        type: 'FeatureCollection',
        features: [...project.sites, site].map((s) => ({
          type: 'Feature',
          geometry: s.geometry,
          properties: { id: s.id, name: s.name, area: s.area_hectares },
        })),
      });
    } catch (err) {
      setError(err.message);
    }
  }

  if (!project) return <Layout><p className="muted">Loading project…</p></Layout>;

  return (
    <Layout>
      <h2 style={{ marginBottom: 2 }}>{project.name}</h2>
      <p className="muted">
        Use the polygon tool on the left of the map to draw a new site, or click an existing
        site to open its analytics.
      </p>
      {error && <div className="error">{error}</div>}

      <div className="split">
        <div ref={container} className="map" />

        <div>
          <div className="card">
            <h3>Add a site</h3>
            {!drawn && <p className="muted">Draw a polygon on the map first.</p>}
            {drawn && (
              <form onSubmit={saveSite}>
                <label>Site name</label>
                <input
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  required
                />
                <label>Land cover</label>
                <select
                  value={form.land_cover}
                  onChange={(e) => setForm({ ...form, land_cover: e.target.value })}
                >
                  <option value="forest">Forest</option>
                  <option value="mangrove">Mangrove</option>
                  <option value="agroforestry">Agroforestry</option>
                  <option value="grassland">Grassland</option>
                  <option value="riparian">Riparian</option>
                  <option value="mixed">Mixed</option>
                </select>
                <button type="submit">Save site</button>
              </form>
            )}
          </div>

          <div className="card">
            <h3>Sites ({project.sites.length})</h3>
            {project.sites.map((s) => (
              <div key={s.id} className="stat">
                <a href={`/sites/${s.id}`}>{s.name}</a>
                <span className="muted">{s.area_hectares} ha</span>
              </div>
            ))}
            {project.sites.length === 0 && <p className="muted">Nothing mapped yet.</p>}
          </div>
        </div>
      </div>
    </Layout>
  );
}
