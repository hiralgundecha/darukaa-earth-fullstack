# Darukaa.Earth

A geospatial dashboard for managing carbon and biodiversity projects. You create a project,
draw site boundaries on a map, and view how each site's metrics have moved over time.

Built for the Darukaa.Earth full-stack hackathon by Hiral Gundecha.

---

## What it does

- Register and log in (JWT)
- Create projects and view them on a dashboard
- Draw site polygons directly on a Mapbox map and save them
- Click any site to see its area, land cover, and metric trends as charts
- Delete sites you no longer need

---

## Architecture

Three parts, deployed separately:

| Layer | Responsibility | Stack |
|---|---|---|
| Frontend | Auth screens, dashboard, map with polygon drawing, charts | React 18 (Vite), Mapbox GL JS, Mapbox GL Draw, Chart.js |
| API | REST endpoints, JWT auth, geometry validation, metric aggregation | Python 3.11, Flask, SQLAlchemy, GeoAlchemy2 |
| Database | Spatial storage and queries, time-series metrics | PostgreSQL 15 + PostGIS 3.3 |

**How a request flows.** The browser holds the JWT in `sessionStorage` and attaches it to every
API call. When you finish drawing a polygon, Mapbox Draw hands back GeoJSON; the API validates
the ring (closed, at least three corners, coordinates in range) before passing it to PostGIS,
which stores it as `GEOMETRY(Polygon, 4326)`.

Area and centroid are **calculated in PostGIS, not in the browser**. That was a deliberate
choice — if two users open the same site on different devices, they see the same number, and
the calculation stays correct if the frontend is ever replaced.

### Project layout

```
backend/
  app/
    __init__.py      app factory, blueprint registration, CORS
    config.py        environment-driven settings
    models.py        SQLAlchemy models
    auth.py          register / login / me
    routes.py        projects, sites, metrics, GeoJSON export
    geometry.py      polygon validation + PostGIS area and centroid
  scripts/seed.py    demo user, projects, sites, 4 years of metrics
  tests/             pytest suite
frontend/
  src/
    api.js           fetch wrapper, token handling, 401 redirect
    pages/           Login, Register, Dashboard, ProjectMap, SiteDetail
    components/      Layout, MetricChart
.github/workflows/   ci.yml, deploy.yml
.husky/              pre-commit, commit-msg
```

---

## Database schema

**users** — `id`, `email` (unique, indexed), `password_hash` (bcrypt), `full_name`, `created_at`

**projects** — `id`, `owner_id` → users, `name`, `description`, `project_type`, `status`, `created_at`

**sites** — `id`, `project_id` → projects, `name`, `land_cover`, `geom GEOMETRY(Polygon, 4326)`, `created_at`

**site_metrics** — `id`, `site_id` → sites, `metric_key`, `value`, `unit`, `recorded_on`

Notes on the design:

- `site_metrics` is stored **long, not wide** — one row per observation rather than one column
  per metric. Adding a new metric type needs no migration, which matters on a platform where
  the science keeps changing. The cost is that chart queries have to group by `metric_key`.
- Composite index on `(site_id, metric_key, recorded_on)` because that is exactly the shape of
  every chart query.
- Foreign keys cascade on delete, so removing a project cleans up its sites and their metrics.

### API endpoints

```
POST   /api/auth/register
POST   /api/auth/login
GET    /api/auth/me
GET    /api/projects
POST   /api/projects
GET    /api/projects/:id                 project + its sites
POST   /api/projects/:id/sites           create a site from GeoJSON
GET    /api/projects/:id/geojson         FeatureCollection for the map
GET    /api/sites/:id                    site + grouped metric series
DELETE /api/sites/:id
GET    /api/health
```

---

## Running it locally

**You need:** Docker, Python 3.11+, Node 18+, and a free Mapbox public token.

```bash
git clone <repo-url>
cd darukaa-earth

# 1. Database
docker compose up -d db

# 2. Backend
cp .env.example .env          # edit JWT_SECRET
cd backend
pip install -r requirements.txt
python scripts/seed.py        # creates tables + demo data
python wsgi.py                # http://localhost:8000

# 3. Frontend (new terminal)
cd frontend
cp ../.env.example .env       # keep only the VITE_ lines, add your Mapbox token
npm install
npm run dev                   # http://localhost:5173
```

Sign in with **reviewer@darukaa.com / darukaa2026**, or register your own account.

Run the tests:

```bash
cd backend && pytest -v
```

---

## CI/CD

### Pre-commit hooks (Husky + lint-staged)

`.husky/pre-commit` runs `lint-staged`, which touches only staged files:

- `frontend/src/**/*.{js,jsx}` → Prettier, then ESLint `--fix`
- `frontend/src/**/*.css` → Prettier
- `backend/**/*.py` → Black, then Ruff `--fix`

`.husky/commit-msg` runs commitlint against Conventional Commits, which is what keeps the
history readable. Because formatting is fixed before the commit lands, CI never fails on
cosmetics alone.

Hooks install automatically via `npm install` at the repo root (the `prepare` script).

### GitHub Actions — `ci.yml`

Runs on every push and PR to `main` and `develop`, two jobs in parallel:

- **backend** — spins up a `postgis/postgis:15-3.3` service container, enables the PostGIS
  extension, runs Ruff and `black --check`, then pytest against a real spatial database. The
  geometry tests would pass against SQLite too, but the auth and query tests would not, so a
  real PostGIS container is worth the extra thirty seconds.
- **frontend** — `npm ci`, Prettier check, ESLint, then a full production build. The build step
  catches things that only break outside dev mode.

### `deploy.yml`

Triggered by a successful CI run on `main` only. Hits deploy hooks for Render (API + database)
and Vercel (frontend). Secrets live in GitHub Actions secrets and the host dashboards —
nothing sensitive is committed, and `.env` is gitignored.

---

## Data

Everything in `scripts/seed.py` is demo data. Site boundaries are polygons drawn over real
locations in the Raigad district of Maharashtra (Gadhi creek near Panvel, and upland plots near
Karjat) so the map renders somewhere real. Metric values are synthetic, but generated inside
ranges that FAO and IPCC report for mangrove and agroforestry systems — a mangrove block
starting near 68 tC/ha and gaining a few tonnes a year is plausible, whereas random numbers
would have made the charts meaningless.

The brief allowed any dataset. I chose synthetic-but-plausible over a real open dataset because
real monitoring data for these specific parcels does not exist, and I would rather the demo be
honestly labelled than quietly wrong.

---

## Trade-offs I made

**Flask over Django.** The app is a small JSON API; Django's admin and ORM conventions would
have been more framework than the problem needs, and GeoAlchemy2 gives direct access to PostGIS
functions. What I gave up is Django's built-in auth, which I had to write by hand.

**PostGIS geometry over storing raw GeoJSON text.** Spatial indexing, server-side area
calculation, and validity checks at the database level. The cost is a heavier local setup —
reviewers need the PostGIS image, not plain Postgres.

**Chart.js over Highcharts.** Both were allowed. Chart.js is MIT licensed with no commercial
restrictions, and for simple time-series it does the job in far less configuration.

**`sessionStorage` for the token, not `localStorage`.** The token clears when the tab closes,
which is a small but real reduction in exposure. A production version should move to an
httpOnly refresh-token cookie; I have noted this as a limitation rather than pretending the
current setup is ideal.

---

## Known limitations

- No refresh tokens. The access token lasts 12 hours and then you sign in again.
- Every authenticated user is effectively an administrator over their own data. There is no
  role system or sharing between users yet.
- Overlapping site polygons within one project are allowed. A real deployment should either
  block them or flag them explicitly.
- Sites you draw yourself start with no metrics, since there is no data-entry screen. The
  seeded demo sites are the ones with charts.
- The free-tier API instance sleeps when idle, so the first request to the live demo can take
  30–50 seconds. After that it is responsive.
