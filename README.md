# CS4182 Computer Graphics — Student Coursework Package

This package contains nine tutorial notebooks and five programming assignments for CS4182 Computer Graphics. The materials follow the lecture sequence and use Python throughout.

## Package contents

```text
CS4182_Student_Coursework_Package/
├── README.md
├── ACADEMIC_INTEGRITY.md
├── requirements.txt
├── tutorials/
│   ├── README.md
│   ├── notebooks/
│   ├── assets/
│   ├── cg_support/
│   └── outputs/
├── assignments/
│   ├── A01_environment_modelling_transformations/
│   ├── A02_projection_visibility_shading_pipeline/
│   ├── A03_ray_tracing_radiosity/
│   ├── A04_antialiasing_realtime_rendering/
│   └── A05_gpu_animation_image_processing/
└── cg_framework/
```

- `tutorials/notebooks/` contains the nine Jupyter notebooks.
- `assignments/` contains the specifications, starter code, public tests, report templates, and demonstrations for the five assignments.
- `cg_framework/` contains supplied support code used by the assignment demonstrations. Do not edit it.
- `outputs/` folders contain reference or generated images and data files.

## Tutorial and assignment sequence

| Tutorials | Tutorial topics | Assignment | Assignment topic | Weight |
|---|---|---|---|---:|
| T1 | Object representation and geometric transformation | A1 | Environment, object modelling, and transformations | 10% |
| T2–T4 | Projection, clipping, visibility, shading, and the rendering pipeline | A2 | Projection, visibility, shading, and the rasterization pipeline | 25% |
| T5 | Ray tracing and simplified radiosity | A3 | Ray tracing and simplified radiosity | 20% |
| T6–T7 | Sampling, anti-aliasing, and real-time rendering | A4 | Anti-aliasing and real-time rendering | 20% |
| T8–T9 | GPU concepts, animation, and image processing | A5 | GPU animation and image processing | 25% |

Complete the relevant tutorials before beginning each assignment.

## Environment setup

Python 3.10 or later is recommended. From the package root, create one environment for all tutorials and assignments:

```bash
python -m venv .venv
source .venv/bin/activate                 # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Do not include `.venv`, cache folders, or generated temporary files in a submission.

## Using the tutorial notebooks

Start Jupyter from the tutorial directory:

```bash
cd tutorials
jupyter lab
```

Open a notebook under `tutorials/notebooks/`. Each notebook contains worked examples, written questions, coding activities marked **Your turn — code**, and short self-checks.

Use **Kernel → Restart Kernel and Run All Cells** to verify the notebook. An unfinished TODO prints `Not attempted yet` without stopping the completed demonstrations. Matplotlib figures appear inside the notebook and are also saved under `tutorials/outputs/`.

The tutorial notebooks demonstrate graphics concepts with NumPy, Matplotlib, Pillow, and small CPU implementations. They do not directly call the OpenGL API.

## Working on an assignment

Each assignment is self-contained. Begin by reading its `ASSIGNMENT.md`, then complete the functions marked `TODO` in `src/student.py` without changing public function names or signatures.

For example, to start Assignment 1:

```bash
cd assignments/A01_environment_modelling_transformations
python environment_check.py
python -m pytest -q
python demo.py
```

The starter tests are expected to fail until the corresponding TODO functions are implemented. Repeat the public tests and demonstration as you work.

The core assignment algorithms use NumPy and can be tested without a graphics context. A1, A2, A4, and A5 also provide an optional OpenGL preview:

```bash
python demo.py --opengl
```

The supplied `cg_framework/` code manages the OpenGL window, shaders, texture presentation, and low-level buffers. VAO, VBO, and EBO setup is not directly assessed. The optional preview requires a desktop graphics environment and working OpenGL drivers.

## Submission checklist

Follow the detailed checklist in each `ASSIGNMENT.md`. Unless the specification states otherwise, submit one ZIP archive containing:

```text
Axx_student_id/
├── src/student.py
├── tests/
├── outputs/
├── README.md
├── report.md
└── requirements.txt
```

Before submission:

1. run `python -m pytest -q` from the assignment directory;
2. run `python demo.py` and inspect the generated output;
3. complete `report.md`;
4. cite all third-party code and assets;
5. disclose any permitted generative-AI assistance; and
6. remove virtual environments, caches, and unrelated large files.

Read `ACADEMIC_INTEGRITY.md` before beginning the assignments.
