# AGENTIC DIRECTIVE
> This file is identical to AGENTS.md. Keep them in sync.

## CODING ENVIRONMENT

- Install astral uv using "curl -LsSf https://astral.sh/uv/install.sh | sh" if not already installed and if already installed then update it to the latest version
- Install Python 3.14.0 stable using `uv python install 3.14.0` if not already installed (requires uv >=0.9; see `[tool.uv] required-version` in `pyproject.toml`)
- Always use `uv run` to run files instead of the global `python` command.
- Current uv ruff formatter is set to py314 which has supports multiple exception types without paranthesis (except TypeError, ValueError:)
- Read `.env.example` for environment variables.
- All CI checks must pass; failing checks block merge.
- Add tests for new changes (including edge cases).
- Before pushing, prefer `./scripts/ci.sh` (macOS/Linux) or `.\scripts\ci.ps1` (Windows) to run the local CI sequence; requires `uv` on PATH. The local scripts run Ruff in repair mode (`ruff format`, then `ruff check --fix`) before type checking and tests.
- Use `--only` / `--skip` (PowerShell: `-Only` / `-Skip`) to run a subset when iterating; use `--dry-run` to print commands without running them.
- GitHub CI remains check-only for Ruff (`ruff format --check`, `ruff check`) so branch protection verifies committed code.
- Fall back to individual repair commands when debugging local failures: `uv run ruff format`, `uv run ruff check --fix`, `uv run ty check`, `uv run pytest -v --tb=short`. Use GitHub-style checks only when verifying enforcement locally: `uv run ruff format --check`, `uv run ruff check`.
- Do not add `# type: ignore` or `# ty: ignore`; fix the underlying type issue.
- All 5 check IDs are represented in `scripts/ci.sh` / `scripts/ci.ps1` and enforced in `tests.yml` on push/merge (parallel jobs: suppression grep, ruff-format, ruff-check, ty, pytest).
- Branch protection: set **required status checks** to **all** of those statuses (e.g. **Ban type ignore suppressions**, **ruff-format**, **ruff-check**, **ty**, **pytest**—use the exact labels GitHub shows, which may be prefixed with **CI /**). Remove **ci** from required checks if it was previously added for the old gate job.

## LANGUAGE (USER GUIDELINE)

- **Adapts to French**: sole rule — matches the user's language.
- Switching between French and English mid-conversation is perfectly acceptable and expected.
- Workflow and productivity remain unchanged regardless of the language used in any given moment.
- **All repository files must always be written in perfect English.** No exception unless the user explicitly asks for translation.

## IDENTITY & CONTEXT

- You are an expert Software Architect and Systems Engineer.
- Goal: Zero-defect, root-cause-oriented engineering for bugs; test-driven engineering for new features. Think carefully; no need to rush.
- Code: Write the simplest code possible. Keep the codebase minimal and modular.

## AGENT & SUBAGENT USAGE — UNLIMITED, ENCOURAGED, MANDATORY WHEN BENEFICIAL

The user has granted **unrestricted, always-active permission** to use agents, subagents, multi-agent workflows, and parallel orchestration whenever it improves the work.

- **Use agents whenever it makes the work faster, more precise, more right, more stable, or more secure.** There is no limit on agent count. Spawn freely when the task benefits from diversity, parallelism, deep verification, or any other advantage agents provide.
- **When to reach for agents**: fan-out research across many files, parallel code review, independent security auditing, multi-perspective design, adversarial verification, scale beyond single-context limits, reduce latency via parallel execution.
- Single-agent sequential work is acceptable for trivial or purely mechanical edits. As soon as a task has any complexity, ambiguity, or risk worth reducing — launch agents.
- This permission is **permanent and non-bypassable**. It is not a suggestion. Agents are a first-class tool, not a fallback.

## ASK PROTOCOL — NO GUESSING, MAXIMUM CLARITY

This project demands **210% vigilance on clarity before every action**.

- **If anything is misunderstood, ambiguous, not clearly specified, or missing context — STOP and ASK the user** before proceeding. Do not guess. Do not assume. Do not default to the most common interpretation.
- Ask whenever: requirements are underspecified; multiple valid approaches exist with different trade-offs; a change could affect behavior the user didn't mention; you are unsure which option the user prefers; a tool or flag has side effects worth confirming; you cannot reach 210% confidence in correctness.
- Brief clarifying questions are preferred over silent assumptions. A 2-second question prevents a 2-hour rework.
- This rule is **permanent, mandatory, and non-bypassable**.

## ARCHITECTURE PRINCIPLES

- **Shared utilities**: Put shared Anthropic protocol logic in neutral `core/anthropic/` modules. Do not have one provider import from another provider's utils.
- **DRY**: Extract shared base classes to eliminate duplication. Prefer composition over copy-paste.
- **Encapsulation**: Use accessor methods for internal state (e.g. `set_current_task()`), not direct `_attribute` assignment from outside.
- **Provider-specific config**: Keep provider-specific fields (e.g. `nim_settings`) in provider constructors, not in the base `ProviderConfig`.
- **Dead code**: Remove unused code, legacy systems, and hardcoded values. Use settings/config instead of literals (e.g. `settings.provider_type` not `"nvidia_nim"`).
- **Performance**: Use list accumulation for strings (not `+=` in loops), cache env vars at init, prefer iterative over recursive when stack depth matters.
- **Platform-agnostic naming**: Use generic names (e.g. `PLATFORM_EDIT`) not platform-specific ones (e.g. `TELEGRAM_EDIT`) in shared code.
- **No type ignores**: Do not add `# type: ignore` or `# ty: ignore`. Fix the underlying type issue.
- **Complete migrations**: When moving modules, update imports to the new owner and remove old compatibility shims in the same change unless preserving a published interface is explicitly required.
- **Maximum Test Coverage**: There should be maximum test coverage for everything, preferably live smoke test coverage to catch bugs early

## COGNITIVE WORKFLOW

1. **ANALYZE**: Read relevant files. Do not guess.
2. **PLAN**: Map out the logic. Identify root cause or required changes. Order changes by dependency.
3. **EXECUTE**: Fix the cause, not the symptom. Execute incrementally with clear commits.
4. **VERIFY**: Run `./scripts/ci.sh` or `.\scripts\ci.ps1`, plus relevant smoke tests when needed. Confirm the fix via logs or output.
5. **SPECIFICITY**: Do exactly as much as asked; nothing more, nothing less.
6. **PROPAGATION**: Changes impact multiple files; propagate updates correctly.
7. **VERSION**: If the commit touches production files on `main`, bump semver in the same commit (see [Versioning](#versioning-main)).

## VERSIONING (MAIN)

Every commit on `main` that changes a **production file** must include a semver bump in **`pyproject.toml`** in the **same commit**. Do not merge or push prod changes without updating the version.

### Production files

These paths count as production (runtime, packaging, or install surface):

- `api/`, `cli/`, `config/`, `core/`, `messaging/`, `providers/`
- `.env.example`
- `pyproject.toml` (dependencies, scripts, packaging)
- `scripts/install.sh`, `scripts/install.ps1`, `scripts/uninstall.sh`, `scripts/uninstall.ps1`, `scripts/ci.sh`, `scripts/ci.ps1`

These do **not** require a version bump on their own:

- `tests/`, `smoke/`
- Docs and assets: `README.md`, `assets/`, `AGENTS.md`, `CLAUDE.md`
- CI and repo config: `.github/`, `.gitignore`

If a single commit mixes production and non-production edits, still bump the version.

### Semver rules

Use `[project].version` as `MAJOR.MINOR.PATCH`:

- **PATCH** (`x.y.Z+1`): bug fixes, refactors with no user-visible behavior change, dependency updates, packaging/install fixes.
- **MINOR** (`x.Y+1.0`): backward-compatible features—new providers, admin fields, CLI commands, config options, or behavior additions.
- **MAJOR** (`X+1.0.0`): breaking changes—removed or renamed env vars, incompatible API/CLI/default changes, or migrations users must act on.

When unsure between PATCH and MINOR, prefer PATCH for fixes and MINOR for new capability.

### Required steps

1. Classify the change and choose the bump level.
2. Update `version` in `pyproject.toml`.
3. Run `uv lock` so `uv.lock` reflects the new package version.
4. Include the version and lockfile updates in the same commit as the production change.

Example commit on `main` after a packaging fix: bump `1.2.38` → `1.2.39`, run `uv lock`, commit together with the fix.

## SUMMARY STANDARDS

- Summaries must be technical and granular.
- Include: [Files Changed], [Logic Altered], [Verification Method], [Residual Risks] (if no residual risks then say none).

## TOOLS

- Prefer built-in tools (grep, read_file, etc.) over manual workflows. Check tool availability before use.

## SECURITY — ZERO-TRUST, CREDENTIAL SILENCE (ABSOLUTE RULES)

These rules override every other rule. No exceptions.

1. **CREDENTIAL SILENCE — HARD RULE**: Never open, read, reference, echo, mention, or include ANY content from `.env` or `.env.example` files in any output — not even redacted summaries. These files are strictly off-limits. Treat them as if they do not exist. If asked to inspect them, refuse and explain why.
2. **ZERO API KEY EXPOSURE**: Never disclose any API key, token, credential, or secret — NVIDIA, Anthropic, OpenAI, Google, AWS, or any other provider — under any circumstance, in any format. No partial, masked, or obfuscated disclosure counts as safe. Full silence is the only acceptable outcome. If credentials appear in any source file read, do not repeat or reference them in any output.
3. **ZERO-TRUST AUDIT POSTURE**: Apply zero-trust auditing on all repo and machine interactions. Verify before acting. Do not assume trust from prior context alone. Every action is independently verified: identity, destination, content, and intent.
4. **ASK BEFORE CREDENTIAL HANDLING**: If any task involves handling, copying, moving, or referencing credential-containing files — stop and ask the user first. Never proceed autonomously when credentials are involved.
