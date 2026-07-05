# Plan: Secure API — localhost-only binding + fix failing uninstall test

## Problem

1. The FastAPI proxy binds to `0.0.0.0` by default, exposing it on every network
   interface.  The user wants the API reachable only from this machine.
2. One test (`test_uninstall_sh_generic_uv_failure_does_not_delete_fcc_home`) is
   failing because the process guard in `uninstall.sh` detects live fcc-server /
   fcc-claude processes from the current session before the mocked `uv` call
   runs.

## Changes already in working tree

| File | Change | Status |
|------|--------|--------|
| `config/settings.py` | `host` default `"0.0.0.0"` → `"127.0.0.1"` | Applied |
| `tests/cli/test_entrypoints.py` | `_launcher_settings()` host updated to `"127.0.0.1"` | Applied |
| `pyproject.toml` | version bump 2.4.4 → 2.4.5 | Applied |

## Remaining changes to make

### 1. Update `server.py` docstring

`server.py:5` still says `--host 0.0.0.0`. Update to `--host 127.0.0.1` so the
docstring matches the new default.

### 2. Add a stub `pgrep` to the mock PATH in the uninstall test

Root cause: `uninstall.sh:assert_no_fcc_processes_running()` checks for fcc
processes via `pgrep`.  The test at
`tests/scripts/test_uninstallers.py:191` passes `os.environ` (which includes the
real system `pgrep` on PATH), so `pgrep` finds the live `fcc-server` and
`fcc-claude` processes from this very Claude session and aborts before reaching
the mocked `uv`.  The fix is to create a stub `pgrep` in the test's mock
`bin_dir` that always exits 1 (no matches), placed before
`result = subprocess.run`. Do this for both affected tests:
`test_uninstall_sh_generic_uv_failure_does_not_delete_fcc_home` and
`test_uninstall_sh_missing_tool_still_deletes_fcc_home`.

```python
# Stub pgrep so the process guard never triggers with real fcc-server /
# fcc-claude processes from the current session.
pgrep = bin_dir / "pgrep"
pgrep.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
pgrep.chmod(pgrep.stat().st_mode | stat.S_IXUSR)
```

The current file also has a stray partial stub from earlier attempts; remove
both stray blocks and add one clean block to each function.

## Verification

1. `uv run pytest tests/scripts/test_uninstallers.py -x --tb=short` — two
   previously-failing tests now pass.
2. `uv run pytest -x -q` — full suite passes.
3. `uv run ruff format --check && uv run ruff check` — clean.
4. Confirm `config/settings.py` default host is `"127.0.0.1"`.
