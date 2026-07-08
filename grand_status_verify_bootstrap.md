# Grand Status / Verify Bootstrap

## Verification points

A key verification checks against the currently installed components:

- `uv` per-project venv is active and on PATH.
- `python` version matches the `[tool.uv] required-version` constraint from `pyproject.toml` if any.
- `[project] dependencies` are installed and lock-file is consistent (`uv.lock` present).
- CI scripts (`scripts/ci.sh`, `scripts/ci.ps1`) are available and executable.
- No `# type: ignore` / `# ty: ignore` suppressions exist in the repo.
- Ruff rules still pass (format + check).
- Type-checker (`ty`) runs clean.
- Pytest completes without error.

## Observability

After `uv run uvicorn` bring the live:

- Log sink: `.log/server.log` TRACE JSON lines via loguru.
- Trace payload `metadata` field must expose structured context keys: `request_id`, `node_id`, `chat_id`, `claude_session_id`, `http_method`, `http_path`.
- Provider integrations emit `provider.request.sent` and `provider.response.completed` events with `gateway_model`, `provider`, `sse_chunks_out`, `sse_bytes_out`.

## Smoke

```bash
uv run python -m pytest -v --tb=short
```

## Upstream

| Label | URL |
|-------|-----|
| GitHub (Th0-oss owner) | https://github.com/Th0-oss/free-claude-code.git |

Default remote labels may differ; verify with `git remote -v`.
