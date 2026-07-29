"""Single source of version truth: installed metadata, falling back to pyproject.toml."""

import tomllib  # Python 3.11+
from importlib.metadata import PackageNotFoundError, version as _dist_version
from pathlib import Path


def get_version(package: str = "pdf-redactor") -> str:
    """Read the version from installed metadata, falling back to pyproject.toml.

    The app runs uninstalled (uv sync --no-install-project), so the metadata
    lookup normally misses and the pyproject.toml fallback is what resolves.
    """
    try:
        return _dist_version(package)
    except PackageNotFoundError:
        for parent in Path(__file__).resolve().parents:
            pyproject = parent / "pyproject.toml"
            if pyproject.exists():
                with pyproject.open("rb") as fh:
                    return tomllib.load(fh)["project"]["version"]
        raise RuntimeError("Could not determine version")
