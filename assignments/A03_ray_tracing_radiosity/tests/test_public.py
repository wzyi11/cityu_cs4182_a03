import importlib
import os

import numpy as np

impl = importlib.import_module(os.environ.get("CS4182_IMPL_MODULE", "src.student"))


def test_central_primary_ray_points_forward():
    origins, directions = impl.generate_primary_rays(3, 3, 60.0)
    np.testing.assert_allclose(origins, 0.0)
    np.testing.assert_allclose(directions[1, 1], [0.0, 0.0, -1.0], atol=1e-7)
    np.testing.assert_allclose(np.linalg.norm(directions, axis=-1), 1.0, atol=1e-7)


def test_ray_sphere_distance_and_miss():
    origins = np.array([[0.0, 0.0, 0.0], [0.0, 3.0, 0.0]])
    directions = np.array([[0.0, 0.0, -1.0], [0.0, 0.0, -1.0]])
    distances = impl.intersect_spheres(origins, directions, np.array([[0.0, 0.0, -5.0]]), np.array([1.0]))
    np.testing.assert_allclose(distances[0, 0], 4.0, atol=1e-7)
    assert np.isinf(distances[1, 0])


def test_nearest_hit_handles_misses():
    indices, distances = impl.nearest_hit(np.array([[3.0, 1.0], [np.inf, np.inf]]))
    assert indices.tolist() == [1, -1]
    np.testing.assert_allclose(distances[0], 1.0)
    assert np.isinf(distances[1])


def test_reflection():
    reflected = impl.reflect(np.array([[1.0, -1.0, 0.0]]) / np.sqrt(2), np.array([[0.0, 1.0, 0.0]]))
    np.testing.assert_allclose(reflected, [[1, 1, 0]] / np.sqrt(2), atol=1e-7)


def test_radiosity_step_and_solver():
    emission = np.array([1.0, 0.0])
    reflectance = np.array([0.5, 0.5])
    factors = np.array([[0.0, 0.2], [0.2, 0.0]])
    first = impl.radiosity_step(emission, reflectance, factors, emission)
    np.testing.assert_allclose(first, [1.0, 0.1])
    final, history = impl.solve_radiosity(emission, reflectance, factors)
    np.testing.assert_allclose(final, np.linalg.solve(np.eye(2) - reflectance[:, None] * factors, emission), atol=1e-6)
    assert len(history) > 1

