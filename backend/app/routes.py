from collections import defaultdict

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from .geometry import InvalidPolygon, geojson_to_geom, site_to_dict
from .models import Project, Site, SiteMetric, db

api_bp = Blueprint("api", __name__, url_prefix="/api")


def current_user_id():
    return int(get_jwt_identity())


def owned_project_or_404(project_id):
    project = Project.query.filter_by(
        id=project_id, owner_id=current_user_id()
    ).first()
    return project


@api_bp.get("/projects")
@jwt_required()
def list_projects():
    projects = (
        Project.query.filter_by(owner_id=current_user_id())
        .order_by(Project.created_at.desc())
        .all()
    )
    return jsonify([p.to_dict() for p in projects])


@api_bp.post("/projects")
@jwt_required()
def create_project():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Project name is required."}), 400

    project = Project(
        owner_id=current_user_id(),
        name=name,
        description=(data.get("description") or "").strip(),
        project_type=data.get("project_type") or "carbon",
    )
    db.session.add(project)
    db.session.commit()
    return jsonify(project.to_dict()), 201


@api_bp.get("/projects/<int:project_id>")
@jwt_required()
def get_project(project_id):
    project = owned_project_or_404(project_id)
    if not project:
        return jsonify({"error": "Project not found."}), 404
    payload = project.to_dict()
    payload["sites"] = [site_to_dict(s) for s in project.sites]
    return jsonify(payload)


@api_bp.post("/projects/<int:project_id>/sites")
@jwt_required()
def create_site(project_id):
    project = owned_project_or_404(project_id)
    if not project:
        return jsonify({"error": "Project not found."}), 404

    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Site name is required."}), 400

    try:
        geom = geojson_to_geom(data.get("geometry") or {})
    except InvalidPolygon as exc:
        return jsonify({"error": str(exc)}), 400

    site = Site(
        project_id=project.id,
        name=name,
        land_cover=data.get("land_cover") or "mixed",
        geom=geom,
    )
    db.session.add(site)
    db.session.commit()
    return jsonify(site_to_dict(site)), 201


@api_bp.get("/sites/<int:site_id>")
@jwt_required()
def get_site(site_id):
    site = (
        Site.query.join(Project)
        .filter(Site.id == site_id, Project.owner_id == current_user_id())
        .first()
    )
    if not site:
        return jsonify({"error": "Site not found."}), 404

    payload = site_to_dict(site)
    payload["project_name"] = site.project.name

    series = defaultdict(list)
    rows = (
        SiteMetric.query.filter_by(site_id=site.id)
        .order_by(SiteMetric.recorded_on)
        .all()
    )
    for row in rows:
        series[row.metric_key].append(
            {"date": row.recorded_on.isoformat(), "value": row.value, "unit": row.unit}
        )
    payload["metrics"] = series
    return jsonify(payload)


@api_bp.delete("/sites/<int:site_id>")
@jwt_required()
def delete_site(site_id):
    site = (
        Site.query.join(Project)
        .filter(Site.id == site_id, Project.owner_id == current_user_id())
        .first()
    )
    if not site:
        return jsonify({"error": "Site not found."}), 404
    db.session.delete(site)
    db.session.commit()
    return jsonify({"deleted": site_id})


@api_bp.get("/projects/<int:project_id>/geojson")
@jwt_required()
def project_geojson(project_id):
    """One FeatureCollection so Mapbox can draw the whole project in a single layer."""
    project = owned_project_or_404(project_id)
    if not project:
        return jsonify({"error": "Project not found."}), 404

    features = []
    for site in project.sites:
        info = site_to_dict(site)
        features.append(
            {
                "type": "Feature",
                "geometry": info.pop("geometry"),
                "properties": info,
            }
        )
    return jsonify({"type": "FeatureCollection", "features": features})
