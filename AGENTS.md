# Agent Guide — Xtherma HA integration

Xtherma heatpump integration for Home Assistant (Python $\ge3.13$, HA `2026.9.x`). Two transports: **REST** (Fernportal, read-only) and **Modbus/TCP** (read+write).

## Rules

1. **Prioritize Interfaces:** When inspecting reference layers such middlewares and generated code, prioritized reading interface files (headers) over implementation.
2. **Git usage:** Never use `git push`. Never delete branches. Never use `git reset`.

## Coding Standards

* **Code Style:** PEP 8, PEP 257, Google-style docstrings, and Ruff formatting.
* **Async/Await Standards**: Built entirely on asynchronous Python (`asyncio`) for non-blocking I/O.

## Testing & Quality Assurance

* Lint check: `scripts/lint`
* Run testsuite with `python -m pytest --timeout=10`

### Updating Snapshots

```bash
pytest tests/test_sensor.py --snapshot-update   # Regenerate per affected test file
pytest tests/test_sensor.py                     # Confirm baseline
```

## Operational Memory Protocol (MANDATORY)

`CONTEXT.md` is the repository's externalized execution state. The
`Operational State` section must reflect the agent's current task state,
not a historical transcript.

### 1. Initialize State
At task start, inspect the existing state and relevant repository context.
Before implementation, replace `Operational State` with the current objective,
intended approach, known constraints, and next step.

### 2. Mutate State
Update `Operational State` whenever a meaningful execution milestone occurs:
- a sub-task is completed;
- a verification milestone is reached;
- an unexpected error or blocker is encountered;
- the implementation approach changes;
- work transitions between major phases.

Do not update for trivial individual actions unless they materially change state.

### 3. Reconcile State
Before relying on previously recorded state, verify it against the repository.
Repository reality takes precedence over stale `CONTEXT.md` entries.

### 4. Finalize State
Before yielding, update `Operational State` with:
- what was completed;
- current verification status;
- remaining blockers;
- the next concrete handoff step.

### Enforcement
A meaningful implementation milestone is incomplete unless the corresponding
`Operational State` update has also been made.