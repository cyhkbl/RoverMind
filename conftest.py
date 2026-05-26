"""Root conftest — adds src packages to sys.path so tests can import without colcon build."""

import sys
from pathlib import Path

_root = Path(__file__).parent
for pkg_dir in (_root / "src").iterdir():
    if pkg_dir.is_dir() and (pkg_dir / "setup.py").exists():
        pkg_src = pkg_dir / pkg_dir.name.replace("-", "_")
        if pkg_src.is_dir() and str(pkg_src.parent) not in sys.path:
            sys.path.insert(0, str(pkg_src.parent))
