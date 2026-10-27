# A3 Report

**Student ID:**  40175691
**Name:**  Zhouyi Wu

## Ray-tracing method

> Explain primary rays, nearest hits, shadow rays, and the single reflection used in your result.

The renderer works **backwards**: instead of projecting triangles onto the screen, it sends one ray from the camera through each pixel and asks what that ray hits. The camera is a pinhole at the origin looking along `-z`, so the image plane is at `z = -1`.

1. **Primary rays.** `generate_primary_rays` creates one ray per pixel. Every ray starts at the origin and points through the **centre** of its pixel (not a corner), which avoids a half-pixel shift. The vertical spread comes from `tan(fov_y / 2)`; the horizontal spread is scaled by `width / height` so the image is not stretched. All directions are normalised to unit length.

2. **Nearest hit.** `intersect_spheres` plugs the ray `o + t·d` into the sphere equation and solves the resulting quadratic. No real solution means a miss (distance `inf`); otherwise the smallest positive distance is the visible surface. `nearest_hit` then picks the smallest distance over all spheres, so each pixel shows the closest object.

3. **Shadow rays.** To test whether a point is lit, the code sends a second ray from that point toward the light. If any sphere is hit before the light, the point is in shadow and only a little ambient light is used. A small offset along the normal stops the ray from hitting its own surface.

4. **Single reflection.** `reflect` mirrors the incoming direction about the surface normal: `d − 2(d·n)n`. The demo follows one reflected ray per visible point and adds a fraction of whatever that ray hits. This gives a simple glossy / colour-bleed effect, with no recursion and no full global illumination.

## Radiosity experiment

> Report the stopping tolerance, number of iterations, final patch values, and whether the sequence converged.

The four-patch system uses emission `E = [1, 0, 0, 0]`, reflectance `ρ = [0.35, 0.65, 0.55, 0.45]`, and the supplied form-factor matrix. `radiosity_step` performs one simultaneous Jacobi update

```
B_new = E + ρ ⊙ (F · B_old)
```

and `solve_radiosity` repeats it until the maximum absolute change falls below `tolerance = 1e-7` (or `max_iterations = 200`).

| Quantity | Result |
|---|---|
| Stopping tolerance | `1e-7` (max absolute update) |
| Iterations to converge | **12** (history holds 13 entries: initial emission + 12 updates) |
| Final radiosity `B` | **`[1.02177, 0.15419, 0.11340, 0.06590]`** |
| Converged? | **Yes** — final update `3.0e-8 < 1e-7` |

The maximum update per iteration falls monotonically, roughly by the spectral radius of `ρF` each step:

```
0.13 → 0.01876 → 0.00622 → 0.00136 → 3.81e-4 → 9.46e-5 → 2.49e-5
→ 6.36e-6 → 1.65e-6 → 4.20e-7 → 1.10e-7 → 3.00e-8
```

The geometric decay confirms the Jacobi iteration is contractive for this (sub-unity `ρF`) system. As an independent check, the converged vector agrees with the direct solution `(I − diag(ρ)F)⁻¹ E` to within `1e-8`. Patch 1 stays near its emitted value because it is the only emitter; the other patches rise to small positive values set by light received from it, exactly as the convergence plot shows.

## Method comparison

> Compare the starting domain, visibility treatment, lighting assumptions, output, and computational cost of rasterization, backward ray tracing, and radiosity.

| Aspect | Rasterization (A2 pipeline) | Backward ray tracing (A3) | Diffuse radiosity (A3) |
|---|---|---|---|
| **Starting domain** | Object/screen space — triangles are projected and filled pixel by pixel | Image space — one ray per pixel generated from the camera | Surface patches — energy exchanged between finite areas via form factors |
| **Visibility treatment** | Per-fragment **depth buffer** (z-buffer) resolves which surface wins | Explicit **ray–object intersection**; nearest positive `t` wins per ray | Encoded in the **form factors** `F_ij` (geometric, view-independent); no per-pixel rays |
| **Lighting assumptions** | **Local** Phong shading; no inter-reflection between objects | Local shading **plus one reflection bounce** (partial global light) | **Global diffuse** energy exchange; view-independent; specular is ignored |
| **Output** | Raster image at display resolution; view-dependent | Per-pixel colour image; view-dependent | Per-patch radiosity values (view-independent); must be shaded/interpolated afterwards |
| **Computational cost** | Low and highly parallel (GPU); cost grows with fragments and overdraw | Grows with `pixels × objects` per bounce; multiplies with each extra bounce | `O(patches²)` form factors + iterative solve; expensive for many patches but **independent of viewpoint** |

The three methods answer different questions. Rasterization is fast but only knows about the surface it happens to be drawing, so it needs shadow maps or extra passes for shadows. Backward ray tracing asks per pixel what it can see and can follow a ray onward, so shadows and reflections come almost for free, at the cost of scaling with resolution and scene size. Radiosity solves for *how much light leaves each surface*, integrating diffuse inter-reflection globally, but it ignores view direction, specular highlights, and the cost grows with the square of the patch count.

## Runtime and reproducibility

> Record the command, image dimensions, machine information, and measured runtime.

```bash
cd assignments/A03_ray_tracing_radiosity
conda activate cs4182
python -m pytest -q   # 5 passed
python demo.py
```

| Item | Value |
|---|---|
| Ray-traced scene | **240 × 180** pixels = **43,200 primary rays** |
| Saved figure | **1050 × 420** px (`outputs/a03_ray_tracing_radiosity.png`) |
| `shade_scene` (best of 3) | **0.049 s** |
| Radiosity solve (best of 3) | **0.00007 s** (12 iterations on 4 patches) |
| Full `python demo.py` wall time | **≈ 3.1 s** (dominated by matplotlib/PIL import and figure rasterisation) |
| CPU | Intel Core Ultra 5 125H, 14 cores / 18 threads |
| Memory | 31.6 GB |
| OS | Windows 11 (build 10.0.26300) |
| Python / NumPy | 3.10.22 / 2.2.6 |

**Reproducibility evidence.** The public test suite passes `5/5`. The demo output was compared against the reference image shipped with the package: after mapping the reference's 436 × 327 scene rectangle back to the 240 × 180 render grid, the two images have a Pearson correlation of **0.99944** and a mean absolute pixel difference of **0.82 / 255**, consistent with resampling and anti-aliasing differences only. The radiosity values also match the reference to five decimals.

## Attribution and AI use declaration

> List external resources and any permitted AI assistance, or write `None`.

- **Tool used:** Claude Code (Anthropic).

- **Prompts or task types:**
  * implementing `reflect` (`TODO(A3.4)`);
  * implementing `solve_radiosity` (`TODO(A3.6)`);
  * helping write the `_normalize` helper that keeps direction vectors at unit length.

- **Files or functions affected:**
  * `src/student.py`: `reflect`, `solve_radiosity`, and the `_normalize` helper.

- **How I verified and understood it:**
  * Ran `"D:/new/minianaconda/envs/cs4182/python.exe" -m pytest -q` — all 5 public tests pass; ran `demo.py` — both panels are generated and the printed final radiosity matches the reference to five decimals.
  * **Reflection:** `r = d − 2(d·n)n` mirrors the incident direction about the normal. I checked that normal incidence reverses the ray, a grazing ray is unchanged, and `_normalize` keeps the result unit length (and leaves a zero vector safe).
  * **Radiosity:** `B = E + ρ ⊙ (F·B)` is one Jacobi update; `solve_radiosity` repeats it and stops when `max|ΔB| < 1e-7`. I checked the converged vector against the direct solution `(I − diag(ρ)F)⁻¹E` and against the 12-iteration sequence above.
  * **Image check:** I compared the rendered scene with the package's reference image (correlation `0.99944`), confirming the geometry and shading agree.
