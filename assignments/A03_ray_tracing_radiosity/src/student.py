"""Assignment 3 student functions."""

from __future__ import annotations

import numpy as np

_EPSILON = 1e-6

# assist method
def _normalize(vectors: np.ndarray) -> np.ndarray:
    """Return unit vectors, leaving zero vectors unchanged."""
    vectors = np.asarray(vectors, dtype=float)
    norms = np.linalg.norm(vectors, axis=-1, keepdims=True)
    norms = np.where(norms == 0.0, 1.0, norms)
    return vectors / norms

# TODO(A3.1)
def generate_primary_rays(height: int, width: int, fov_y_degrees: float):
    """Return origins and unit directions for a pinhole camera at the origin.

    The image plane is in the negative-z direction. Returned arrays have shape
    ``(height, width, 3)``.
    """
    if height <= 0 or width <= 0:
        raise ValueError("height and width must be positive")
    aspect = width / height
    half_height = np.tan(np.radians(fov_y_degrees) / 2.0)
    half_width = half_height * aspect
    # Pixel-centre coordinates: x runs left to right, y top to bottom.
    cols = ((np.arange(width) + 0.5) / width * 2.0 - 1.0) * half_width
    rows = (1.0 - (np.arange(height) + 0.5) / height * 2.0) * half_height
    x, y = np.meshgrid(cols, rows)  # each (height, width)
    directions = np.stack([x, y, -np.ones_like(x)], axis=-1)
    origins = np.zeros((height, width, 3))
    return origins, _normalize(directions)

# TODO(A3.2)
def intersect_spheres(
    ray_origins: np.ndarray,
    ray_directions: np.ndarray,
    centres: np.ndarray,
    radii: np.ndarray,
) -> np.ndarray:
    """Return the nearest positive distance to every sphere for every ray.

    The returned shape is ``ray_origins.shape[:-1] + (number_of_spheres,)``.
    Missing intersections are represented by ``np.inf``.
    """
    origins = np.asarray(ray_origins, dtype=float)
    directions = np.asarray(ray_directions, dtype=float)
    centres = np.asarray(centres, dtype=float)
    radii = np.asarray(radii, dtype=float)

    oc = origins[..., None, :] - centres  # (..., S, 3)
    d = directions[..., None, :]  # broadcasts against (..., S, 3)
    a = np.sum(d * d, axis=-1)
    b = 2.0 * np.sum(oc * d, axis=-1)
    c = np.sum(oc * oc, axis=-1) - radii ** 2
    discriminant = b * b - 4.0 * a * c

    hits = discriminant >= 0.0
    sqrt_disc = np.sqrt(np.where(hits, discriminant, 0.0))
    t_near = (-b - sqrt_disc) / (2.0 * a)
    t_far = (-b + sqrt_disc) / (2.0 * a)
    # Prefer the near root; fall back to the far root (ray starts inside).
    t = np.where(hits & (t_near > _EPSILON), t_near, t_far)
    valid = hits & (t > _EPSILON)
    return np.where(valid, t, np.inf)

#TODO(A3.3)
def nearest_hit(distances: np.ndarray):
    """Return the nearest sphere index and distance for each ray.

    Use index -1 and distance inf when a ray misses every sphere.
    """
    distances = np.asarray(distances, dtype=float)
    has_hit = np.isfinite(distances).any(axis=-1)
    indices = np.where(has_hit, np.argmin(distances, axis=-1), -1)
    nearest = np.where(has_hit, np.min(distances, axis=-1), np.inf)
    return indices, nearest

# TODO(A3.4)
def reflect(directions: np.ndarray, normals: np.ndarray) -> np.ndarray:
    """Reflect incident unit directions about unit surface normals."""
    directions = np.asarray(directions, dtype=float)
    normals = np.asarray(normals, dtype=float)
    dot = np.sum(directions * normals, axis=-1, keepdims=True)
    return _normalize(directions - 2.0 * dot * normals)

# TODO(A3.5)
def radiosity_step(emission: np.ndarray, reflectance: np.ndarray, form_factors: np.ndarray, radiosity: np.ndarray) -> np.ndarray:
    """Perform one Jacobi radiosity update: B = E + rho * (F @ B)."""
    emission = np.asarray(emission, dtype=float)
    reflectance = np.asarray(reflectance, dtype=float)
    form_factors = np.asarray(form_factors, dtype=float)
    radiosity = np.asarray(radiosity, dtype=float)

    n = emission.shape[-1]
    if reflectance.shape[-1] != n or radiosity.shape[-1] != n:
        raise ValueError("emission, reflectance, and radiosity must share the last axis")
    if form_factors.shape[-2:] != (n, n):
        raise ValueError("form_factors must be (n, n) matching the patch count")
    return emission + reflectance * (form_factors @ radiosity)

# TODO(A3.6)
def solve_radiosity(
    emission: np.ndarray,
    reflectance: np.ndarray,
    form_factors: np.ndarray,
    tolerance: float = 1e-7,
    max_iterations: int = 200,
):
    """Iterate radiosity until the maximum absolute update is below tolerance.

    Return ``(final_radiosity, history)`` where history includes the initial
    emission and every subsequent iterate.
    """
    emission = np.asarray(emission, dtype=float)
    radiosity = emission.copy()
    history = [radiosity.copy()]
    for _ in range(max_iterations):
        updated = radiosity_step(emission, reflectance, form_factors, radiosity)
        delta = np.max(np.abs(updated - radiosity))
        radiosity = updated
        history.append(radiosity.copy())
        if delta < tolerance:
            break
    return radiosity, history
