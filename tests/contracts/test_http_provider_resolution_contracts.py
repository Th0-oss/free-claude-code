import ast
from pathlib import Path

from tests.contracts.test_import_boundaries import _resolve_relative_import

_PROCESS_CACHE_ABS = "api.provider_process_cache"


def _illegal_process_cache_module_imports(repo_root: Path, path: Path) -> list[str]:
    """Return human-readable offenses if this file imports the process-cache module."""

    offenses: list[str] = []
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    dotted_prefix = f"{_PROCESS_CACHE_ABS}."
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.name
                if name == _PROCESS_CACHE_ABS or name.startswith(dotted_prefix):
                    offenses.append(f"import {name}")
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                if node.module:
                    module = node.module
                    imported = ", ".join(a.name for a in node.names)
                    pulls_cache_from_api_pkg = module == "api" and (
                        "provider_process_cache" in {a.name for a in node.names}
                    )
                    is_cache_module_import = module == _PROCESS_CACHE_ABS or (
                        module.startswith(dotted_prefix)
                    )
                    if pulls_cache_from_api_pkg or is_cache_module_import:
                        offenses.append(f"from {module} import {imported}")
                continue

            resolved = _resolve_relative_import(repo_root, path, node)
            if resolved == _PROCESS_CACHE_ABS or (
                resolved is not None and resolved.startswith(dotted_prefix)
            ):
                imported = ", ".join(a.name for a in node.names)
                offenses.append(
                    f"relative import resolves to `{resolved}` ({imported})"
                )
    return offenses


def test_live_api_handlers_do_not_call_process_cached_provider_helpers() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    watched = ("api/routes.py", "api/services.py")

    needles = (
        "get_process_cached_provider(",
        "get_process_cached_provider_for_type(",
    )
    for relative in watched:
        body = (repo_root / relative).read_text(encoding="utf-8")
        banned_hits = [token for token in needles if token in body]
        assert banned_hits == [], f"{relative} must avoid {banned_hits!r}"


_ALLOWED_PROCESS_CACHE_MODULES = frozenset(
    {
        "api/dependencies.py",
        "api/provider_process_cache.py",
    }
)
"""Modules that may reference PROCESS_PROVIDERS / provider_process_cache module name."""


def test_api_must_not_touch_process_providers_outside_allowlist() -> None:
    """Prevent bypassing resolve_provider/process-cache façade from random api modules."""
    repo_root = Path(__file__).resolve().parents[2]
    needles = ("provider_process_cache", "PROCESS_PROVIDERS")
    offenders: list[str] = []
    api_root = repo_root / "api"
    for path in sorted(api_root.rglob("*.py")):
        rel = path.relative_to(repo_root).as_posix()
        if rel in _ALLOWED_PROCESS_CACHE_MODULES:
            continue

        illegal_imports = _illegal_process_cache_module_imports(repo_root, path)
        if illegal_imports:
            offenses = "; ".join(illegal_imports)
            offenders.append(f"{rel}: illegal process-cache imports ({offenses})")

        text = path.read_text(encoding="utf-8")
        hits = [n for n in needles if n in text]
        if hits:
            offenders.append(f"{rel}: text mentions {hits!r}")
    allowed = ", ".join(sorted(_ALLOWED_PROCESS_CACHE_MODULES))
    assert offenders == [], (
        "Touch PROCESS_PROVIDERS / provider_process_cache only when implementing "
        f"dependency wiring or owning the cache module (allowed files: {allowed}).\n\n"
        + "\n".join(offenders)
    )
