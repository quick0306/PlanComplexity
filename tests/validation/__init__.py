"""Test package shim for validation discovery."""

import sys
from pathlib import Path

_PACKAGE_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _PACKAGE_DIR.parents[1]
_REAL_PACKAGE_DIR = _REPO_ROOT / "validation"
_REAL_INIT = _REAL_PACKAGE_DIR / "__init__.py"

if __name__ == "validation":
    module = sys.modules[__name__]
    module.__file__ = str(_REAL_INIT)
    module.__path__ = [str(_REAL_PACKAGE_DIR), str(_PACKAGE_DIR)]
    if module.__spec__ is not None:
        module.__spec__.origin = module.__file__
        module.__spec__.submodule_search_locations = module.__path__
    exec(compile(_REAL_INIT.read_text(encoding="utf-8"), module.__file__, "exec"), module.__dict__)
