"""Checks for the domain geometry and wall profile."""
import numpy as np
from generate_geometry import make_geometry


def test_wall_width_and_flat_interior():
    centres, edges, depth = make_geometry(n=200)
    assert centres[0] == 2500.0
    assert edges[-1] == 1_000_000.0
    assert depth[0, 100] < depth[1, 100] < depth[8, 100] < 4000.0
    assert depth[9, 100] == 4000.0
    assert depth[100, 100] == 4000.0


def test_geometry_symmetry_and_legacy_wall_values():
    _, _, depth = make_geometry(n=200)
    np.testing.assert_array_equal(depth, depth[::-1, :])
    np.testing.assert_array_equal(depth, depth[:, ::-1])
    np.testing.assert_allclose(depth[0, 100], 35.66529492455418)
    _, _, old_domain = make_geometry(n=100)
    np.testing.assert_array_equal(depth[:10, 100], old_domain[:10, 50])
