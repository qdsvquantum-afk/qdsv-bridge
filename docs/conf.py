from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import qdsv_bridge  # noqa: E402


project = "QDSV Bridge"
author = "QDSV / Qruba"
copyright = "2026, QDSV / Qruba"
release = qdsv_bridge.__version__
version = release

extensions = [
    "myst_parser",
    "qiskit_sphinx_theme",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "qiskit-ecosystem"
html_title = f"{project} {release}"
html_static_path = ["_static"]
html_theme_options = {
    "sidebar_qiskit_ecosystem_member": True,
}

myst_heading_anchors = 3
autodoc_typehints = "description"
napoleon_google_docstring = True
napoleon_numpy_docstring = True
