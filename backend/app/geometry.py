"""Helpers that keep all geometry work in PostGIS rather than in the browser."""

from geoalchemy2.shape import to_shape
from sqlalchemy import func

from .models import Site, db


class InvalidPolygon(Exception):
    pass


def validate_ring(coordinates):
    """Basic shape checks before the polygon is handed to PostGIS."""
    if not coordinates or not isinstance(coordinates, list):
        raise InvalidPolygon("Polygon coordinates are missing.")
    ring = coordinates[0]
    if len(ring) < 4:
        raise InvalidPolygon("A polygon needs at least three distinct corners.")
    if ring[0] != ring[-1]:
        raise InvalidPolygon("The polygon ring must be closed.")
    for point in ring:
        lng, lat = point[0], point[1]
        if not (-180 <= lng <= 180 and -90 <= lat <= 90):
            raise InvalidPolygon("Coordinates fall outside valid lat/long bounds.")
    return True


def geojson_to_geom(geojson):
    """Convert GeoJSON from Mapbox Draw into a PostGIS geometry value."""
    if geojson.get("type") != "Polygon":
        raise InvalidPolygon("Only single polygons are supported.")
    validate_ring(geojson.get("coordinates"))
    import json

    return func.ST_SetSRID(func.ST_GeomFromGeoJSON(json.dumps(geojson)), 4326)


def site_to_dict(site, with_geometry=True):
    """Area and centroid are computed by PostGIS so every client agrees."""
    area_m2, centroid_x, centroid_y = (
        db.session.query(
            func.ST_Area(func.ST_Transform(Site.geom, 3857)),
            func.ST_X(func.ST_Centroid(Site.geom)),
            func.ST_Y(func.ST_Centroid(Site.geom)),
        )
        .filter(Site.id == site.id)
        .one()
    )
    payload = {
        "id": site.id,
        "project_id": site.project_id,
        "name": site.name,
        "land_cover": site.land_cover,
        "area_hectares": round((area_m2 or 0) / 10000, 2),
        "centroid": [centroid_x, centroid_y],
        "created_at": site.created_at.isoformat(),
    }
    if with_geometry:
        payload["geometry"] = to_shape(site.geom).__geo_interface__
    return payload
