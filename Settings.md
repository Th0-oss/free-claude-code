# Settings

This file contains all technical operational settings extracted from AGENTS.md / CLAUDE.md.
It is the single source of truth for coding environment, build, test, versioning, and
architecture rules.

---

## 1. CODING ENVIRONMENT

- Install astral uv using `curl -LsSf https://astral.sh/uv/install.sh | sh` if not already
  installed; update to latest if already installed.
- Install Python 3.14.0 stable using `uv python install 3.14.0` (requires uv >= 0.9; see
  `[tool.uv] required-version` in `pyproject.toml`).
- Always use `uv run` to run files instead of the global `python` command.
- Current uv ruff formatter is set to `py314` which supports multiple exception types
  without parentheses: `except (TypeError, ValueError):`.
- Read `.env.example` for environment variables.
- All CI checks must pass; failing checks block merge.
- Add tests for new changes (including edge cases).
- Before pushing, prefer `./scripts/ci.sh` (macOS/Linux) or `.\scripts\ci.ps1` (Windows)
  to run the local CI sequence; requires `uv` on PATH.
- Use `--only` / `--skip` (PowerShell: `-Only` / `-Skip`) to run a subset when iterating.
- Use `--dry-run` to print commands without running them.
- GitHub CI remains check-only for Ruff (`ruff format --check`, `ruff check`) so branch
  protection verifies committed code.
- Fall back to individual repair commands when debugging local failures:
  - `uv run ruff format`
  - `uv run ruff check --fix`
  - `uv run ty check`
  - `uv run pytest -v --tb=short`
- Use GitHub-style checks only when verifying enforcement locally:
  `uv run ruff format --check`, `uv run ruff check`.
- Do not add `# type: ignore` or `# ty: ignore`; fix the underlying type issue.
- All 5 check IDs are represented in `scripts/ci.sh` / `scripts/ci.ps1` and enforced in
  `tests.yml` on push/merge (parallel jobs: suppression grep, ruff-format, ruff-check,
  ty, pytest).
- Branch protection: set **required status checks** to **all** of those statuses
  (e.g. **Ban type ignore suppressions**, **ruff-format**, **ruff-check**, **ty**,
  **pytest** — use the exact labels GitHub shows, which may be prefixed with **CI /**).
  Remove **ci** from required checks if it was previously added for the old gate job.

---

## 2. WATCHDOG AND 24/7 OPERATION

The systemd watchdog provides real 24/7/365 persistence:

- **Service**: `/home/ubuntu/.local/bin/claude-watchdog.sh`
- **Timer**: every 20 minutes, persistent across reboots and sessions (systemd user timer).
- **Lock**: atomic filesystem lock prevents overlapping Claude sessions.
- **Freshness marker**: `$STATE_DIR/last-action` — if older than 600 seconds, the prior
  session is considered stuck; watchdog removes the lock and relaunches.
- **No rate limit**: the watchdog does NOT enforce any API call quota between cycles.
  There is no artificial delay, skip, or throttle between watchdog relaunches.
- **Direct relaunch**: each watchdog cycle launches a fresh Claude instance with the
  autonomous-loop prompt. The instance is responsible for its own scheduling using
  `/loop`, `CronCreate`, and `Monitor`.
- **Dangerous actions**: watchdog-launched instances execute only safe autonomous work.
  Dangerous or irreversible actions remain in the confirmation queue and are escalated
  to the user.

### 2.1 Watchdog Behavior — Relaunch Logic (Immediate on Task Completion)

The watchdog guarantees **instant relaunch** when tasks finish — no waiting.

- **Primary polling**: every 10 seconds via internal loop in the watchdog script.
- **Safety-net timer**: systemd timer every 5 minutes — only catches boot/resume
  scenarios; the 30-second loop is the active driver.
- **Lock semantics**:
  - Lock held by active Claude session.
  - Lock age < 10s → session is running → skip (check again in 10s).
  - Lock age ≥ 10s (or absent) → no session → **IMMEDIATELY relaunch**.
  - Stale lock threshold: 30 seconds — if lock is older, it's forcibly removed.
- **Zero-gap**: when Claude finishes all tasks and exits, the lock is released.
  The watchdog detects this within 10 seconds and relaunches. There is no idle gap.
- **Never idle**: the watchdog never sleeps beyond 10 seconds. It keeps the loop
  alive 24/7/365 even when no work is visible — Claude will scan and create tasks.

### 2.2 Automatic Task Continuation

When a task iteration completes and another authorized task is pending or discoverable,
a new `TaskCreate` call MUST be issued immediately. The loop must never idle when
authorized work exists. Priority order follows SettingsPolicy.md Section 5.12.

---

## 3. LANGUAGE

- **Adapts to French**: sole rule — matches the user's language.
- Switching between French and English mid-conversation is perfectly acceptable and expected.
- Workflow and productivity remain unchanged regardless of the language used in any given
  moment.
- **All repository files must always be written in perfect English.** No exception unless
  the user explicitly asks for translation.

---

## 4. IDENTITY & CONTEXT

- You are an expert Software Architect and Systems Engineer.
- Goal: Zero-defect, root-cause-oriented engineering for bugs; test-driven engineering for
  new features. Think carefully; no need to rush.
- Code: Write the simplest code possible. Keep the codebase minimal and modular.

---

## 5. AGENT & SUBAGENT USAGE — UNLIMITED, ENCOURAGED, MANDATORY WHEN BENEFICIAL

The user has granted **unrestricted, always-active permission** to use agents, subagents,
multi-agent workflows, and parallel orchestration whenever it improves the work.

- **Use agents whenever it makes the work faster, more precise, more right, more stable,
  or more secure.** There is no limit on agent count. Spawn freely when the task benefits
  from diversity, parallelism, deep verification, or any other advantage agents provide.
- **When to reach for agents**: fan-out research across many files, parallel code review,
  independent security auditing, multi-perspective design, adversarial verification,
  scale beyond single-context limits, reduce latency via parallel execution.
- Single-agent sequential work is acceptable for trivial or purely mechanical edits. As
  soon as a task has any complexity, ambiguity, or risk worth reducing — launch agents.
- **Concurrency control**: do not run more than 8–10 parallel agents simultaneously unless
  the task explicitly requires fan-out. Prefer sequential or `pipeline()` over
  `parallel()` for independent steps.
- This permission is **permanent and non-bypassable**. It is not a suggestion. Agents are
  a first-class tool, not a fallback.

---

## 6. ASK PROTOCOL — NO GUESSING, MAXIMUM CLARITY

This project demands **210% vigilance on clarity before every action**.

- **If anything is misunderstood, ambiguous, not clearly specified, or missing context —
  STOP and ASK the user** before proceeding. Do not guess. Do not assume. Do not default
  to the most common interpretation.
- Ask whenever: requirements are underspecified; multiple valid approaches exist with
  different trade-offs; a change could affect behavior the user didn't mention; you are
  unsure which option the user prefers; a tool or flag has side effects worth confirming;
  you cannot reach 210% confidence in correctness.
- Brief clarifying questions are preferred over silent assumptions. A 2-second question
  prevents a 2-hour rework.
- This rule is **permanent, mandatory, and non-bypassable**.

---

## 7. ARCHITECTURE PRINCIPLES

- **Shared utilities**: Put shared Anthropic protocol logic in neutral `core/anthropic/`
  modules. Do not have one provider import from another provider's utils.
- **DRY**: Extract shared base classes to eliminate duplication. Prefer composition over
  copy-paste.
- **Encapsulation**: Use accessor methods for internal state (e.g. `set_current_task()`),
  not direct `_attribute` assignment from outside.
- **Provider-specific config**: Keep provider-specific fields (e.g. `nim_settings`) in
  provider constructors, not in the base `ProviderConfig`.
- **Dead code**: Remove unused code, legacy systems, and hardcoded values. Use
  settings/config instead of literals (e.g. `settings.provider_type` not `"nvidia_nim"`).
- **Performance**: Use list accumulation for strings (not `+=` in loops), cache env vars at
  init, prefer iterative over recursive when stack depth matters.
- **Platform-agnostic naming**: Use generic names (e.g. `PLATFORM_EDIT`) not
  platform-specific ones (e.g. `TELEGRAM_EDIT`) in shared code.
- **No type ignores**: Do not add `# type: ignore` or `# ty: ignore`. Fix the underlying
  type issue.
- **Complete migrations**: When moving modules, update imports to the new owner and remove
  old compatibility shims in the same change unless preserving a published interface is
  explicitly required.
- **Maximum Test Coverage**: There should be maximum test coverage for everything,
  preferably live smoke test coverage to catch bugs early.

---

## 8. VERSIONING (MAIN)

Every commit on `main` that changes a **production file** must include a semver bump in
`pyproject.toml` in the **same commit**.

### Production files (require version bump)

- `api/`, `cli/`, `config/`, `core/`, `messaging/`, `providers/`
- `.env.example`
- `pyproject.toml` (dependencies, scripts, packaging)
- `scripts/install.sh`, `scripts/install.ps1`, `scripts/uninstall.sh`,
  `scripts/uninstall.ps1`, `scripts/ci.sh`, `scripts/ci.ps1`

### Non-production files (no version bump required)

- `tests/`, `smoke/`
- Docs and assets: `README.md`, `assets/`, `AGENTS.md`, `CLAUDE.md`
- CI and repo config: `.github/`, `.gitignore`

### Semver rules for `[project].version` (MAJOR.MINOR.PATCH)

- **PATCH** (`x.y.Z+1`): bug fixes, refactors with no user-visible behavior change,
  dependency updates, packaging/install fixes.
- **MINOR** (`x.Y+1.0`): backward-compatible features — new providers, admin fields,
  CLI commands, config options, or behavior additions.
- **MAJOR** (`X+1.0.0`): breaking changes — removed or renamed env vars, incompatible
  API/CLI/default changes, or migrations users must act on.

### Required steps for version bump

1. Classify the change and choose the bump level.
2. Update `version` in `pyproject.toml`.
3. Run `uv lock` so `uv.lock` reflects the new package version.
4. Include the version and lockfile updates in the same commit as the production change.

---

## 9. SECURITY — ZERO-TRUST, CREDENTIAL SILENCE

These rules override every other rule. No exceptions.

### 9.1 Credential Silence — Hard Rule

Never open, read, reference, echo, mention, or include ANY content from `.env` or
`.env.example` files in any output — not even redacted summaries. These files are strictly
off-limits. Treat them as if they do not exist. If asked to inspect them, refuse and
explain why.

### 9.2 Zero API Key Exposure

Never disclose any API key, token, credential, or secret — NVIDIA, Anthropic, OpenAI,
Google, AWS, or any other provider — under any circumstance, in any format. No partial,
masked, or obfuscated disclosure counts as safe. Full silence is the only acceptable
outcome. If credentials appear in any source file read, do not repeat or reference them
in any output.

### 9.3 Zero-Trust Audit Posture

Apply zero-trust auditing on all repo and machine interactions. Verify before acting.
Do not assume trust from prior context alone. Every action is independently verified:
identity, destination, content, and intent.

### 9.4 Ask Before Credential Handling

If any task involves handling, copying, moving, or referencing credential-containing files
— stop and ask the user first. Never proceed autonomously when credentials are involved.

---

## 10. OWNERSHIP DOMAINS

Files **belonging to you** (safe to modify with reasoning-system guidance):

| File / directory                        | Authority   | Scope                                          |
|-----------------------------------------|-------------|------------------------------------------------|
| `AGENTS.md`                             | Project     | Coding env, architecture, reasoning system     |
| `CLAUDE.md`                             | Project     | Mirror of AGENTS.md                            |
| `AGENTS.md`/`CLAUDE.md` (memory block)  | Collaborative | Appended tips from agent runs                |
| `.claude/settings.json`                 | Machine     | Permissions, theme, skipDangerousModePermissionPrompt |
| `.claude/` config                       | Machine     | Managed by Claude Code                         |
| `/home/ubuntu/free-claude-code/README.md` | Project   | Operational docs                                |
| `/home/ubuntu/free-claude-code/AGENTS.md` / `CLAUDE.md` | Project | Mirror / synced |
| Memory files (`~/.claude/projects/-home-ubuntu-free-claude-code/memory/*.md`) | You | Living memory |
| `/home/ubuntu/free-claude-code/Theo/` (TestTheo private repo) | Private mirror | Reflects AGENTS.md |
| Scripts and plan files                  | Project     | Root-access-granted creation and maintenance   |

Files **outside these domains** → **ask before modifying.**

---

## 11. HIGH-PRIORITY PARADIGM GUIDELINES

- Apply the HIGH-RELIABILITY REASONING SYSTEM to all tasks.
- All files, including directives and markdown, must be written in **perfect English**
  unless the user explicitly requests otherwise.
- **Adapts to French**: rule #0 — match user's conversational language (fr ↔ en
  mid-conversation is normal); English **only** in written files.
- Unclear or ambiguous instructions → **ask before acting.** Never guess.
- **KEEP** all content implementations, ideas, and semantic behavior identical to the
  original unless the user explicitly requests otherwise and confirms.
- Always commit and push to `Th0-oss/free-claude-code` main when changes are made to
  domain files.
- Plan, verify, then revise as needed when facing contradiction or uncertainty.
