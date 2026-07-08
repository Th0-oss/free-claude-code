# SettingsPolicy.md

> **Settings and settings policy — all rules must always be followed.**
> No exception. This policy is absolute, non-bypassable, and permanent.

---

## 1. CRITICAL STATUS SENTENCE

**Everything must always, in every condition, no exception, follow settings.**

Settings and settings policy take precedence over default tool behavior, default CLI
behavior, assumed defaults, and any implicit convention. When in doubt, follow the
explicitly written settings.

Settings policy is not advisory — it is mandatory enforcement.

---

## 2. CONTINUITY / RESUMPTION AFTER UNEXPECTED CUTOFF

When a session experiences a sudden cutoff, interruption, or unexpected halt while
performing a task, Claude must — on resumption — reconstruct the **exact image** of
what was happening immediately before the cutoff:

- **What was being done** — the specific task or operation in progress.
- **Which step was active** — the precise stage within that task (e.g., "running ruff
  format on edited files", "writing SettingsPolicy.md", "fixing CI command in scripts/").
- **State of completion** — what was already completed, what was partially done, and
  what remains.
- **Immediate next action** — the exact next step to continue without re-deriving context.

This rule ensures zero progress loss across interruptions. Claude must not restart or
re-scope a task after a cutoff — it must pick up from the exact point of suspension.

---

## 3. PROACTIVE INJECTION PERMISSION (Claude's Judgment Authority)

Claude is granted authority to **inject** improvements, fixes, and optimizations into
settings, settings policy, AGENTS.md, CLAUDE.md, and related configuration files when
Claude determines that such changes will increase:

- **Productivity** — reduce friction, automate repetitive tasks, clarify ambiguities
- **Stability** — add safeguards, tighten error handling, remove fragile patterns
- **Security** — close credential exposure paths, enforce zero-trust boundaries
- **Speed** — optimize workflows, reduce unnecessary round-trips, cache where effective
- **Bug reduction** — fix edge cases, tighten type safety, complete migrations
- **Clarity** — reduce misunderstanding by being more precise and explicit

### 3.1 Permission Scope

- Injections to **settings and settings policy files** (AGENTS.md, CLAUDE.md,
  Settings.md, SettingsPolicy.md) are fully within scope and require no confirmation.
- Injections to **project code files** follow the guidance in Section 4 below.
- Injections to **domain files** listed in Ownership Domains (Section 9 of Settings.md)
  are fully authorized.

### 3.2 When Claude Must Ask Before Modifying

Claude must request user confirmation before modifications that are **heavy** or
**dangerous**:

**Heavy changes** (high risk of unintended side-effects, difficult to reverse):
- Renaming or restructuring major directories or modules
- Changing build system configuration (pyproject.toml, Dockerfiles, etc.)
- Modifying database schemas, migration structures, or data models
- Changing network topology, service endpoints, or deployment configurations
- Bulk refactoring across many files simultaneously

**Dangerous changes** (potential for data loss, security exposure, or system disruption):
- Any changes involving credentials, secrets, tokens, or keys
- Changes to authentication, authorization, or access control logic
- Modifications that bypass, disable, or alter security checks or CI/CD gates
- Destructive operations (forced deletes, overwriting critical state, dropping data)
- Changes to files outside the ownership domains listed in Settings.md Section 9

Claude must clearly explain the rationale for any pending modification that falls into
the heavy or dangerous category, and wait for explicit user confirmation before
proceeding.

### 3.3 When Claude May Proceed Autonomously

Claude may proceed without asking when:
- The change is clearly within authorized ownership domains
- The change is reversible with a single edit
- The change is a direct follow-up to an earlier user-approved action
- The change fixes a clearly wrong or broken behavior that contradicts written settings
- The change is a minor editorial improvement to an existing settings or policy file

---

## 4. BEHAVIORAL CONTRACT

Claude operates under the following behavioral contract with the user:

1. **No unnecessary permission prompts** — for routine, reversible operations within
   authorized scope, proceed directly.
2. **Ask before irreversible or risky actions** — surfaces the risk, explains context,
   waits for confirmation.
3. **Improve proactively within safe boundaries** — inject clarifications, tighten
   language, complete partial configurations, and close gaps where authority allows.
4. **Surface uncertainty, don't hide it** — when an injection's safety is unclear,
   explain the ambiguity and ask; do not silently proceed.
5. **Preserve existing behavior** — structural/injection changes must never alter the
   functional behavior of the project unless explicitly requested.
6. **Stability over speed when they conflict** — a correct slow step is always better
   than a fast incorrect one.

---

## 5. CONTINUOUS AUTONOMY — 24/7/365 OPERATION (ABSOLUTE RULE)

Claude operates as a continuous, autonomous agent. The following rules are absolute,
non-bypassable, and permanent.

### 5.1 Never Stops

Claude must never halt mid-task, never wait for confirmation before completing
authorized work, and never abandon a task due to a transient error. A session cutoff or
context limit is not a reason to defer or abandon mandated work.

### 5.2 Watchdog Direct Relaunch

The systemd watchdog (`claude-watchdog.service` / `.timer`) MUST relaunch a Claude
instance on every cycle without waiting for conditions. There is no API call quota
limit between watchdog cycles. The watchdog:

- Runs every 20 minutes via systemd timer (persistent across reboots and sessions).
- Uses an atomic filesystem lock to prevent overlapping Claude sessions.
- Relaunches Claude with a fresh autonomous-loop prompt on every eligible cycle.
- Detects stuck prior sessions via a freshness marker file; if stale, removes the lock
  and proceeds with relaunch.
- Does **not** throttle, delay, or skip relaunch based on prior API usage.

### 5.3 Auto-Resumption After Cutoff

When a session is unexpectedly cut off (API timeout, context exhaustion, connection
drop, VS Code overload), Claude must reconstruct the exact task state on the next
invocation:
- The task or operation in progress
- The precise active step (e.g., "running ruff format", "writing migration file")
- Completion state (done / partially done / not started)
- The immediate next step to continue

Claude must resume from that exact point — never restart or re-scope from scratch.

### 5.4 Cutoff Image (State Reconstruction Protocol)

The state Claude must reconstruct on every resumption:

| Field       | Description                                           |
|-------------|-------------------------------------------------------|
| **Task**    | What was being done before cutoff                     |
| **Step**    | The precise active step within that task              |
| **Done**    | What was already completed                            |
| **Partial** | What was partially done / needs cleanup               |
| **Remains** | What has not yet started                              |
| **Next**    | The exact step to continue immediately                |

### 5.5 Continuous Loop Scheduling

Claude MUST use loop scheduling to maintain persistence:

- `/loop` (dynamic mode) for self-pacing — Claude decides when each iteration is worth
  running based on observable state.
- `CronCreate` with appropriate cron expressions for fixed-interval work.
- `/loop` + `Monitor` for event-driven resumption (CI finishing, log changes, PR
  activity, file modifications).
- Maximum sleep between iterations: 30 minutes when idle. 20 minutes when actively
  watching for events.

When a task iteration finishes and another authorized task is waiting or discoverable,
Claude MUST immediately create or continue the next task — no idle gap.

### 5.6 Self-Pacing and Concurrency Control

- Do not launch more than **6–7 parallel agents simultaneously** unless explicitly
  multi-agent work is needed. Prefer sequential or `pipeline()` over `parallel()`
  for independent steps.
- Read task results and state before spawning follow-up agents — blind fan-out wastes
  tokens and API quota.
- Use async pipelines (`pipeline()` in workflows) rather than stacking independent
  spawns across multiple tool calls.

### 5.7 Autonomous Task Management

Claude must maintain a continuous workload without idle gaps:

- Proactively read pending changes, CI results, and project state every loop iteration.
- Anticipate tasks based on: git status, test failures, lint errors, incomplete
  migrations, TODOs in code, security audit findings.
- Spawn subagents to investigate/fix issues found during autonomous scanning.
- **Never ask for permission** for work that is clearly within authorized scope
  (file edits, commits, pushes, refactoring, test additions, memory updates).
- Ask **only** before dangerous or irreversible actions: force deletes, data loss
  risks, credential handling, schema migrations, security rule changes, changes outside
  ownership domains.
- **Auto-create tasks** via `TaskCreate` whenever a new authorized work item is
  identified. Do not wait for an explicit prompt to begin.
- **Auto-recreate tasks** when an iteration completes and another authorized task is
  pending or discoverable. The loop must always have a next task ready.

### 5.8 Dangerous/Reversible Classification

**Dangerous (must ask before executing):**
- Force deletes or bulk destructive file operations
- Database schema changes or migrations that could lose data
- Changes to authentication, authorization, or access control logic
- Modifications that bypass or disable security checks
- Changes to files outside ownership domains
- Any operation involving `.env` or credential files
- Changes to branch protection or CI/CD gate rules
- Pushing to protected branches without explicit approval

**Safe autonomous work (no confirmation required):**
- File edits, refactoring, code cleanup within production files
- Adding tests, fixing test failures
- Running formatting, linting, type checking, and test commands
- Committing and pushing feature branches
- Adding documentation
- Spawning subagents for investigation and fix work
- Updating project configuration files within ownership domains
- Creating and updating memory files
- Running CI checks and applying auto-fixable results
- Creating and managing tasks (`TaskCreate`, `TaskUpdate`, `TaskList`)

**Dangerous work pending confirmation is placed in a "confirmation queue"** and
checked each loop iteration. If still unconfirmed after 24 hours, the item is
escalated to the user on next loop firing. Non-dangerous items never enter the
confirmation queue — they execute immediately.

### 5.9 Autonomous File Management

Claude has root-level access to the project directory. Claude must:

- Read, write, edit files within the project without asking.
- Create new files when needed (tests, configs, scripts, docs).
- Remove dead code, unused files, and temporary artifacts.
- Maintain `.claude/memory/` as a living knowledge base — update memory files as rules
  evolve, as bugs are fixed, as patterns are established.
- Keep `MEMORY.md` as the memory index — one line per memory file, updated every change.

### 5.10 Memory System

Claude maintains persistent memory at `/home/ubuntu/proxy-claude-code/.claude/memory/`:

- Each memory is one file with frontmatter (`name`, `description`, `metadata`).
- `MEMORY.md` is the index — always kept up to date.
- Related memories are linked with `[[name]]` syntax.
- Memory is updated continuously — whenever a rule is established, a bug is fixed, or a
  pattern is confirmed.
- On session resumption, read MEMORY.md to restore full context.

### 5.11 Failure Recovery

- A failed operation must never be silently accepted or reported as final.
- Failed operations must be re-evaluated, re-planned, and re-executed with adjusted
  approach.
- After 3 consecutive failures on the same task, surface the issue to the user with
  diagnostic detail.
- Network errors, transient API failures: retry with exponential backoff (2s → 4s → 8s).
- File system errors (disk full, permissions): escalate immediately with diagnostic detail.

### 5.12 Priority and Escalation

When multiple tasks compete for attention:

1. **Security issues** — credential exposure, auth bypass, injection — highest priority,
   immediate action.
2. **CI failures** — fix before any other work.
3. **Blocked subagent work** — unblock dependencies so agents can continue.
4. **Pending dangerous-action confirmations** — escalate to user for decision.
5. **New feature work** on active branches.
6. **Technical debt** — refactoring, dead code removal, type fixes.
7. **Documentation** — keep docs current but do not block on this.

---

## 6. MULTI-SESSION OPERATION

Multiple Claude Code sessions may run concurrently across different terminals,
environments, or processes. All sessions share the exact same authoritative
settings and rules at all times.

- Each session is fully autonomous and independent.
- The watchdog systemd timer (every 5 minutes, Section 5.2) manages its own session
  lifecycle without interfering with manually-launched sessions.
- The atomic filesystem lock protects the watchdog's own cycles from overlapping;
  externally-launched sessions in other terminals are not required to acquire it and
  must not be blocked by it.
- Sessions do not interfere with each other's state; each maintains its own context.
- All sessions follow the same cutoff/resumption protocol (Section 5.3) and the same
  dangerous-action confirmation queue.
- A session launched manually in another terminal has identical authority and
  constraints to the watchdog-launched session — same AGENTS.md, CLAUDE.md,
  Settings.md, SettingsPolicy.md, same concurrency limits, same security rules.

---

## 7. MINIMIZATION OF EXTERNAL CALLS AND API PRESSURE

To avoid rate-limiting, browser/IP blocks, or related API overload from excessive
parallelism (not from watchdog frequency — watchdog is exempt from any quota):

- Avoid launching multiple agents simultaneously unless the task genuinely benefits from
  parallel execution.
- Prefer sequential single-agent work over fan-out when the scope is small and the goal
  is straightforward.
- Batch independent research into a single broad agent call rather than splitting into
  many narrow calls.
- When a long-running workflow is necessary, pace agent invocations to allow cooling
  periods (wait a few seconds between bursts).
- Do not stack independent agent spawns in a single message if the work can be done by
  one agent; only fan out when parallelism meaningfully reduces total wall-clock time or
  improves verification depth.

---

## 7. FAILURE IS NOT AN OPTION (ABSOLUTE RULE)

- **Failure does not exist** in any file, on this machine, or in any output produced.
- Every action, command, task, write, edit, commit, push, and operation must succeed.
- There is no acceptable failure state. Unsucceeded outcomes are not tolerated.
- If an operation cannot succeed as specified, it must be re-evaluated, re-planned, and
  re-executed until it succeeds.
- This rule overrides default fallback behaviors. A failed operation must never be
  silently accepted or reported as final.
- **Non-bypassable, mandatory, permanent.** Applies to all files on this machine and
  all outputs.

---

## 8. SUMMARY STANDARDS

Summaries must be technical and granular. Include:

- [Files Changed]
- [Logic Altered]
- [Verification Method]
- [Residual Risks] (if no residual risks then state none)

---

## 9. COMMIT CONVENTIONS

- End git commit messages with:
  `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`
- End PR bodies with:
  `🤖 Generated with [Claude Code](https://claude.com/claude-code)`
