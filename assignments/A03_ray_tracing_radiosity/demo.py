"""Render the controlled A3 scene and radiosity convergence plot."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from cg_framework.figures import load_implementation, save_image

impl = load_implementation("src.student")


def shade_scene(height=180, width=240):
    origins, directions = impl.generate_primary_rays(height, width, 52.0)
    centres = np.array([[-0.85, -0.1, -4.3], [0.9, 0.0, -4.8], [0.0, -101.0, -4.0]])
    radii = np.array([0.95, 1.05, 100.0])
    colours = np.array([[0.85, 0.18, 0.12], [0.10, 0.45, 0.90], [0.55, 0.58, 0.62]])
    distances = impl.intersect_spheres(origins, directions, centres, radii)
    hit_index, hit_distance = impl.nearest_hit(distances)
    image = np.full((height, width, 3), [0.025, 0.035, 0.06])
    mask = hit_index >= 0
    points = origins[mask] + hit_distance[mask, None] * directions[mask]
    normals = points - centres[hit_index[mask]]
    normals /= np.linalg.norm(normals, axis=-1, keepdims=True)
    light = np.array([-3.0, 4.5, -1.5])
    to_light = light - points
    light_distance = np.linalg.norm(to_light, axis=-1)
    light_direction = to_light / light_distance[:, None]
    shadow_origins = points + normals * 1e-4
    shadow_distances = impl.intersect_spheres(shadow_origins, light_direction, centres, radii)
    in_shadow = np.any(shadow_distances < light_distance[:, None], axis=-1)
    diffuse = np.maximum(np.sum(normals * light_direction, axis=-1), 0.0)
    view = -directions[mask]
    reflected_light = impl.reflect(-light_direction, normals)
    specular = np.maximum(np.sum(reflected_light * view, axis=-1), 0.0) ** 32
    lit = colours[hit_index[mask]] * (0.10 + 0.85 * diffuse[:, None]) + 0.25 * specular[:, None]
    lit[in_shadow] = colours[hit_index[mask]][in_shadow] * 0.10
    reflected_rays = impl.reflect(directions[mask], normals)
    reflected_distances = impl.intersect_spheres(points + normals * 1e-4, reflected_rays, centres, radii)
    reflected_index, _ = impl.nearest_hit(reflected_distances)
    reflected_mask = reflected_index >= 0
    lit[reflected_mask] += 0.18 * colours[reflected_index[reflected_mask]]
    image[mask] = np.clip(lit, 0, 1)
    return image


def radiosity_history():
    emission = np.array([1.0, 0.0, 0.0, 0.0])
    reflectance = np.array([0.35, 0.65, 0.55, 0.45])
    form_factors = np.array([
        [0.0, 0.24, 0.17, 0.09], [0.20, 0.0, 0.22, 0.12],
        [0.16, 0.20, 0.0, 0.18], [0.10, 0.14, 0.20, 0.0],
    ])
    return impl.solve_radiosity(emission, reflectance, form_factors)


def main():
    image = shade_scene()
    final, history = radiosity_history()
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
    axes[0].imshow(image)
    axes[0].set_title("Backward ray tracing")
    axes[0].axis("off")
    history = np.asarray(history)
    for patch in range(history.shape[1]):
        axes[1].plot(history[:, patch], marker="o", ms=3, label=f"Patch {patch + 1}")
    axes[1].set(title="Radiosity convergence", xlabel="Iteration", ylabel="Radiosity")
    axes[1].legend()
    fig.tight_layout()
    fig.canvas.draw()
    combined = np.asarray(fig.canvas.buffer_rgba())[..., :3]
    output = save_image("outputs/a03_ray_tracing_radiosity.png", combined)
    plt.close(fig)
    print(f"Saved {output}; final radiosity = {np.round(final, 5).tolist()}")


if __name__ == "__main__":
    main()
