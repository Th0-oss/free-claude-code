# Full Proxy Playbook — Th0-oss/free-claude-code

## Identity
This is the **free-claude-code** proxy gateway: a local Anthropic API proxy / gateway
that translates Claude-compatible requests into upstream provider calls
(Anthropic native, NVIDIA NIM, OpenAI-compatible, GitHub Models, Cohere, HuggingFace,
SambaNova, and future adapters).

## Setup

```bash
# 1. prerequisites (macOS)
brew install uv

# 2. install / sync
cd /home/ubuntu/proxy-claude-code
uv sync

# 3. environment
cp .env.example .env   # fill values

# 4. lint + type + test
./scripts/ci.sh --skip ci_grep   # macOS/Linux
.\scripts\ci.ps1 -Skip ci_grep   # Windows
```

## Runtime

```bash
uv run uvicorn server:app --host 0.0.0.0 --port 8082
```

Point any Anthropic-compatible client at the proxy base URL.

## Branch model

| Branch | Purpose |
|--------|---------|
| `main` | Production. Every commit bumps `[project].version` in `pyproject.toml`. |
| `feature-*` | Short-lived feature / fix branches. PR → main. |

## CI gates (required)
1. `ci_grep` — no `# type: ignore` or `# ty: ignore` suppressions
2. `ruff_format` — `ruff format --check`
3. `ruff_check` — `ruff check`
4. `ty` — `uv run ty check`
5. `pytest` — `uv run python -m pytest -v --tb=short`

## Commit authors
Co-authored-by line for tooling:
`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
`

## Security / Credential facade
- Never open, read, reference, Echo, mention, or include ANY content from `.env` (or `.env.example`) in output. Treat as non-existent.
- Zero API key exposure: never disclose any API key, token, credential, or secret in this playbook or in any produced artifact.
