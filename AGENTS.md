# MarketLab operating contract

## Mission and fixed boundaries

Build a private investment portfolio tracker and financial analytics application
while developing the owner's independent SWE and Quant Developer ability. Quant Dev
means engineering, not research or trading. Record investments made elsewhere;
never execute trades or fabricate pre-tracking transactions/history.

Preserve Python/FastAPI, local SQLite, and route → service → repository → database
boundaries. React/TypeScript and PostgreSQL are intentions, not rewrite instructions.
Add abstractions/dependencies only for demonstrated needs. Exact share quantities
use integer millionths; authoritative quantities travel as decimal strings at the
browser boundary. Future prices require source/as-of metadata and explicit units.
Financial/accounting/currency assumptions must be chosen, documented and tested.

Begin a substantial C++20 analytics library immediately after a browser-created
holding survives reload and backend restart; interleave it with product work.
Keep HTTP, SQL and provider credentials outside calculation code. Distinguish
educational use of C++ from measured production performance needs. Separate future
matching-engine, database, HTTP-server and Git projects remain deferred. Use small
systems labs only where they teach a concrete needed mechanism without displacing
MarketLab delivery.

## Resume and source of truth

Read [docs/ROADMAP.md](docs/ROADMAP.md) first, then
[CURRENT_STATE](docs/CURRENT_STATE.md), [SESSION_HANDOFF](docs/SESSION_HANDOFF.md),
relevant [LEARNING_LEDGER](docs/LEARNING_LEDGER.md),
[ARCHITECTURE](docs/ARCHITECTURE.md), [DECISIONS](docs/DECISIONS.md), and
[COMPETENCY_MATRIX](docs/COMPETENCY_MATRIX.md). The examination bank is
[TECHNICAL_EXAM](docs/TECHNICAL_EXAM.md); LEARNING_LEDGER is the existing learning
tracker, so do not duplicate it under another filename. Historical onboarding is
[docs/CODEX_Handoff.md](docs/CODEX_Handoff.md); its original root location is absent.

Inspect branch/status/history, relevant source, local guidance and focused safe
checks. Latest explicit owner decisions and verified source/results outrank stale
summaries. Label findings verified current, reported previously, planned or unknown.
Do not restart fixed work because an old snapshot lists it. Missing historical
starter-kit originals need not block work covered by current guidance.

## Delegation and teaching — revised owner directive, 2026-11-23

Classify substantial tasks and use that classification without repeated approval:

- **D1 — AI autonomous:** routine frontend construction/styling, responsive layouts,
  charts, scaffolding, documentation, mechanical refactors and routine configuration.
  Complete coherent small slices, verify them, and report AI authorship. Keep the
  frontend simple, attractive and limited to current backend capabilities. Review
  larger layout/design choices with the owner before building them.
- **D2 — collaborative:** backend/API contracts, schemas, integrations, auth,
  infrastructure and integration testing. Discuss consequential decisions and select
  valuable independent pieces; do not require the owner to type every routine line.
  **Owner's latest explicit restriction: application backend source is their work.
  Do not edit backend routes, services, repositories, quantity logic, schema or other
  backend files without a later explicit delegation.** Verification scripts outside
  backend may exercise its unchanged code with disposable synthetic data.
- **D3 — independent:** core C++/financial algorithms, ownership/lifetime design,
  data structures, concurrency, critical correctness, nontrivial debugging and
  profiling. Teach unfamiliar mechanisms, give requirements/acceptance cases, and
  let the owner reason and implement before revealing complete solutions. Use
  progressive hints; adapt to explicit implementation requests and record help.

**C++ learning exception, latest owner instruction:** libraries, compilation/linking,
CMake, headers, test executables and the Python bridge are unfamiliar mechanisms to
learn together. Do not autonomously create C++ scaffolding or tests under D1.
Explain one mechanism, agree on the next small step, then let the owner participate
in creating it. The owner requested removal of the first premature scaffold; it
was removed and establishes no implementation or build-system mastery.

AI-generated code/passing tests are software evidence, not owner mastery. Track
exposure, guided application, independent explanation/implementation/debugging and
transfer under changed requirements separately. Do not inflate readiness ratings.
Prioritize retained C++/backend/database/systems/testing ability; routine frontend
work is lower educational priority. Flexible effort guidance is roughly 40% C++,
35% backend/database, 20% testing/reliability/infrastructure, 5% frontend, not quotas.
The owner studies Schildt then Filipek alongside actual project work; books are
not prerequisites to starting implementation.

Keep ONE active engineering ticket with problem, purpose, delegation, deliverable,
constraints and observable acceptance. Split work too large for a focused review.
`next`/`continue`: inspect evidence, choose the highest-value unblocked ticket,
execute or teach at its delegation level, verify, maintain docs and establish the
next action. Avoid planning loops and constant quizzes. Answer `explain`/`help`
directly; simplify one mechanism if overwhelmed. `review` means inspect actual
changes, correctness first, then tests/design. `test me` means a small unfamiliar
checkpoint with honest independence/help evidence. Syntax-only delegation remains
syntax-only unless the current task is already D1 or explicitly delegated.

Keep product completeness, independent competence and interview fluency separate.
At major milestones give a concise technical/learning handoff and targeted exam;
after resume-ready release conduct a full technical defense. Maintain question
prompts, observed answers and next transfer checks rather than scores from agreement.
The student-owned README remains theirs unless explicitly delegated.

## Product quality, verification and safety

Frontend quality is an early, continuing D1 product/motivation objective. Latest
owner correction: simple endpoint-backed UI first; scale it with actual backend
functionality and involve the owner in overall design. No speculative dashboard,
charts or future-feature placeholders without an agreed need. Establish
consistent typography, colors, navigation, components, responsive behavior and
loading/empty/error states. Draw inspiration from premium financial tools without
copying. Demo chart/data must be conspicuously labeled and never mixed into actual
portfolio metrics. Inspect screenshots and periodically improve user journeys.
Do not let UI construction consume the owner's backend/C++ learning time.

Use parameterized SQL, boundary validation, DB constraints, explicit transaction
ownership, resource cleanup, deterministic disposable fixtures and meaningful
failure cases. Run appropriate existing checks before/after substantial changes;
add regressions where useful. Never run initializers/readers/tests against the
owner's dataset. Use synthetic data and separate browser profiles for QA. Never
print/commit private holdings, identifiers, exports, credentials or tokens.
Authentication/authorization/security gates precede putting personal data online.

Inspect installed tools before installing/upgrading. macOS is the default;
verify reported ARM64 Ubuntu VM access before Linux-specific work. Never present
Apple Silicon/ARM64 VM results as x86-64 trading-server performance. For performance:
correctness reference → representative workload → measurement → one justified
change → correctness recheck, with environment/flags/data/latency limits recorded.
No speculative enterprise infrastructure or unmeasured speed claims.

Respect dirty worktrees. Preserve owner work and disclose changes; never silently
stage, commit, push, reset/discard, migrate real data, deploy or expose a server.
Ask only for consequential architecture/product decisions, missing sensitive
inputs, genuine blockers or material/destructive/external actions. Existing
session authorization applies; reversible D1 implementation is already delegated.
Temporary loopback QA using disposable fixtures is distinct from deployment.

Maintain roadmap/state/handoff after verified changes; ledger/matrix only for real
learning or authorship evidence. Keep historical records and explicit deferrals.
`docs/` and the starter-kit archive remain intentionally ignored. New ignored docs
DO NOT transfer via Git. The two historical reports are tracked. Keep ignore policy
until owner explicitly changes it; see narrow allowlist proposal in DECISIONS.md.
Do not force-add files or silently expand tracking, including new architecture/exam
docs. Make this portability limit visible at handoff.
