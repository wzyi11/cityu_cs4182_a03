# Assignment 3: Ray Tracing and Simplified Radiosity

**Suggested period:** Weeks 6–8  
**Weight:** 20%  
**Aligned tutorial:** T5  
**Estimated workload:** 16–20 hours

## Purpose

Implement a controlled backward ray tracer and a small diffuse radiosity experiment. The assignment emphasises the flow of visibility and energy computations, not acceleration structures or production rendering.

## Learning outcomes

You should be able to:

1. generate primary rays from a pinhole camera;
2. compute and select the nearest valid ray–sphere intersection;
3. use shadow rays to determine direct-light visibility;
4. compute a reflected direction;
5. explain the difference between ray tracing and diffuse radiosity; and
6. iterate a small radiosity system and assess convergence.

## Student tasks

Complete every `TODO` in `src/student.py`:

1. `generate_primary_rays`
2. `intersect_spheres`
3. `nearest_hit`
4. `reflect`
5. `radiosity_step`
6. `solve_radiosity`

The supplied demo uses these functions to render a low-resolution sphere scene with local Phong illumination, shadow rays, and one reflection bounce. It also produces a radiosity convergence plot for four diffuse patches. You do not need to implement a BVH, triangle mesh acceleration, Monte Carlo integration, or a high-resolution renderer.

## Required commands

```bash
python -m pytest -q
python demo.py
```

## Submission

Submit the completed code, tests, `outputs/a03_ray_tracing_radiosity.png`, a runtime measurement, and `report.md`.

## Assessment

| Criterion | Marks |
|---|---:|
| Primary ray generation | 15 |
| Intersection and nearest-hit selection | 25 |
| Shadow and one-bounce reflection behaviour | 20 |
| Radiosity update and convergence | 20 |
| Method comparison and numerical evidence | 10 |
| Tests, reproducibility, and code quality | 10 |
| **Total** | **100** |

## Checkpoint

One week before the deadline, demonstrate correct primary rays, a sphere silhouette, and nearest-hit selection.

## Minimum viable submission

Primary rays, intersection, nearest-hit selection, and radiosity iteration pass the public tests; the no-reflection reference scene is saved.

