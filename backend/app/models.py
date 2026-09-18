from datetime import datetime, date

import bcrypt
from flask_sqlalchemy import SQLAlchemy
from geoalchemy2 import Geometry

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    projects = db.relationship("Project", back_populates="owner", cascade="all, delete")

    def set_password(self, raw):
        self.password_hash = bcrypt.hashpw(raw.encode(), bcrypt.gensalt()).decode()

    def check_password(self, raw):
        return bcrypt.checkpw(raw.encode(), self.password_hash.encode())


class Project(db.Model):
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, default="")
    project_type = db.Column(db.String(40), default="carbon")
    status = db.Column(db.String(20), default="active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    owner = db.relationship("User", back_populates="projects")
    sites = db.relationship("Site", back_populates="project", cascade="all, delete")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "project_type": self.project_type,
            "status": self.status,
            "site_count": len(self.sites),
            "created_at": self.created_at.isoformat(),
        }


class Site(db.Model):
    __tablename__ = "sites"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    name = db.Column(db.String(160), nullable=False)
    land_cover = db.Column(db.String(60), default="mixed")
    geom = db.Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    project = db.relationship("Project", back_populates="sites")
    metrics = db.relationship("SiteMetric", back_populates="site", cascade="all, delete")


class SiteMetric(db.Model):
    __tablename__ = "site_metrics"
    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(
        db.Integer, db.ForeignKey("sites.id", ondelete="CASCADE"), nullable=False
    )
    metric_key = db.Column(db.String(60), nullable=False)
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(30), default="")
    recorded_on = db.Column(db.Date, default=date.today, nullable=False)

    site = db.relationship("Site", back_populates="metrics")

    __table_args__ = (
        db.Index("ix_metric_lookup", "site_id", "metric_key", "recorded_on"),
    )

    def to_dict(self):
        return {
            "metric_key": self.metric_key,
            "value": self.value,
            "unit": self.unit,
            "recorded_on": self.recorded_on.isoformat(),
        }
