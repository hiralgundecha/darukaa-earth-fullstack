import pytest

from app.geometry import InvalidPolygon, validate_ring


def test_accepts_a_closed_square():
    ring = [[[73.1, 18.9], [73.2, 18.9], [73.2, 19.0], [73.1, 19.0], [73.1, 18.9]]]
    assert validate_ring(ring) is True


def test_rejects_an_open_ring():
    ring = [[[73.1, 18.9], [73.2, 18.9], [73.2, 19.0], [73.1, 19.0]]]
    with pytest.raises(InvalidPolygon):
        validate_ring(ring)


def test_rejects_too_few_points():
    ring = [[[73.1, 18.9], [73.2, 18.9], [73.1, 18.9]]]
    with pytest.raises(InvalidPolygon):
        validate_ring(ring)


def test_rejects_out_of_range_coordinates():
    ring = [[[273.1, 18.9], [73.2, 18.9], [73.2, 19.0], [73.1, 19.0], [273.1, 18.9]]]
    with pytest.raises(InvalidPolygon):
        validate_ring(ring)
