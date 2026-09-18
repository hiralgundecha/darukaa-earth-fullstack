"""Seeds a demo account with two projects, four sites and three years of metrics.

Site boundaries are hand-drawn polygons over real locations in the Raigad and
Thane districts of Maharashtra. Metric values are synthetic but generated inside
ranges reported by FAO and IPCC for these land-cover types, so the charts show a
believable trend instead of random noise.
"""

import json
import random
import sys
from datetime import date
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app import create_app  # noqa: E402
from app.models import Project, Site, SiteMetric, User, db  # noqa: E402
from sqlalchemy import func  # noqa: E402

random.seed(42)

SITES = [
    {
        "project": "Panvel Mangrove Restoration",
        "name": "Gadhi Creek Block A",
        "land_cover": "mangrove",
        "ring": [[73.108, 18.984], [73.122, 18.984], [73.122, 18.995], [73.108, 18.995], [73.108, 18.984]],
        "baseline": {"carbon_stock": 68.0, "canopy_cover": 42.0, "species_richness": 24.0},
        "growth": {"carbon_stock": 3.4, "canopy_cover": 4.5, "species_richness": 1.6},
    },
    {
        "project": "Panvel Mangrove Restoration",
        "name": "Gadhi Creek Block B",
        "land_cover": "mangrove",
        "ring": [[73.126, 18.976], [73.140, 18.976], [73.140, 18.988], [73.126, 18.988], [73.126, 18.976]],
        "baseline": {"carbon_stock": 51.0, "canopy_cover": 28.0, "species_richness": 17.0},
        "growth": {"carbon_stock": 4.1, "canopy_cover": 5.2, "species_richness": 2.1},
    },
    {
        "project": "Karjat Agroforestry Pilot",
        "name": "Neral Upland Plot",
        "land_cover": "agroforestry",
        "ring": [[73.312, 18.928], [73.330, 18.928], [73.330, 18.942], [73.312, 18.942], [73.312, 18.928]],
        "baseline": {"carbon_stock": 22.0, "canopy_cover": 11.0, "species_richness": 9.0},
        "growth": {"carbon_stock": 2.2, "canopy_cover": 3.8, "species_richness": 1.3},
    },
    {
        "project": "Karjat Agroforestry Pilot",
        "name": "Kalamb Riparian Strip",
        "land_cover": "riparian",
        "ring": [[73.288, 18.902], [73.302, 18.902], [73.302, 18.914], [73.288, 18.914], [73.288, 18.902]],
        "baseline": {"carbon_stock": 34.0, "canopy_cover": 19.0, "species_richness": 14.0},
        "growth": {"carbon_stock": 2.8, "canopy_cover": 4.1, "species_richness": 1.8},
    },
]

UNITS = {
    "carbon_stock": "tC/ha",
    "canopy_cover": "%",
    "species_richness": "species",
}


def polygon(ring):
    geojson = json.dumps({"type": "Polygon", "coordinates": [ring]})
    return func.ST_SetSRID(func.ST_GeomFromGeoJSON(geojson), 4326)


def run():
    app = create_app()
    with app.app_context():
        db.create_all()

        if User.query.filter_by(email="reviewer@darukaa.com").first():
            print("Seed data already present. Nothing to do.")
            return

        user = User(email="reviewer@darukaa.com", full_name="Darukaa Reviewer")
        user.set_password("darukaa2026")
        db.session.add(user)
        db.session.flush()

        projects = {}
        for spec in SITES:
            if spec["project"] not in projects:
                project = Project(
                    owner_id=user.id,
                    name=spec["project"],
                    description="Demo project seeded with synthetic monitoring data.",
                    project_type="mixed",
                )
                db.session.add(project)
                db.session.flush()
                projects[spec["project"]] = project

            site = Site(
                project_id=projects[spec["project"]].id,
                name=spec["name"],
                land_cover=spec["land_cover"],
                geom=polygon(spec["ring"]),
            )
            db.session.add(site)
            db.session.flush()

            for year_offset in range(4):
                for key, base in spec["baseline"].items():
                    drift = random.uniform(-0.6, 0.6)
                    value = base + spec["growth"][key] * year_offset + drift
                    db.session.add(
                        SiteMetric(
                            site_id=site.id,
                            metric_key=key,
                            value=round(value, 2),
                            unit=UNITS[key],
                            recorded_on=date(2023 + year_offset, 3, 31),
                        )
                    )

        db.session.commit()
        print("Seeded: reviewer@darukaa.com / darukaa2026")


if __name__ == "__main__":
    run()
