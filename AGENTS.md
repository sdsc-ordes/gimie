# Agent Instructions

Guidelines for AI agents working in the Swiss Data Science Center (SDSC) codebase.

## General values

- Explicit over Implicit: Code should be readable and obvious. Avoid "magic" logic.
- Robustness: Prioritize error handling and edge cases over happy-path-only code.
- Statelessness: Avoid mutable global state. Prefer pure functions.
- Testability: Code must be designed to be easily tested (dependency injection, small units).
- Conciseness: Prefer self-documenting code and terse documentation without filler.
- Modularity: Aim for components with low coupling and high cohesion. 

## Project structure

When creating directories, default to our standard project structure, unless the project has an existing alternative.

- `docs`: All documentation-related files.
- `examples`: Examples showing how to use the software.
- `external`: Imported third party resources.
- `src`: Where your source code lives.
- `tools`: All configurations and scripts which are not part of the source.
  - `configs`: config for tools (e.g. formatters, linters).
  - `images`: `Containerfile` definitions of OCI images.
  - `just`: just modules (e.g. image.just).
  - `nix`: Nix flake and code.
  - `ci`: CI related tooling/scripts.
  - `scripts`: Additional scripts.

## Toolchain

Use the project's existing toolchain when available. Otherwise, default to the following.

* `just` as command runner.
* `nix` flakes for devShells.
* `podman` for OCI images.
* `prek` as git-hook manager.
* `vendir` to manage external dependencies.
* For python components: `uv`, `ruff`.
* For javascript components: `pnpm`.

## Rules by Topic

These general rules define our high level development practices.
For framework-specific recommendations, refer to specific skills.

### Code Style

- All imports/dependencies should be at the top of the file rather than inside functions.
- Use named placeholders in format strings ("{index}"), not positional ("{}").
- Rule of three: at the third repetition, extract an abstraction.
- Only the public, user-facing contract (API + config formats) needs stability.
  Internal interfaces may change freely; mark them as internal so the boundary is clear.

### Error Handling

Failures are part of a function's contract, expressed in its return/error type.

- Never abort the process on recoverable conditions. Model failures as values or
  typed errors the caller can handle, not as abrupt termination.
- Ban "assume success" shortcuts that convert a recoverable error into a crash
  (ignoring a returned error).
- Propagate, don't swallow: attach context at each
  layer, and preserve the underlying cause so the root is recoverable from the trace.

### Testing

- Every component that generates or handles data carries correctness requirements.
- Apply the cheapest verification (static analysis / type checking) to all code;
  treat its failures as build failures.
- Property-based tests are the primary workhorse: generate many inputs and assert
  invariants rather than hand-picked cases.
- Where call order matters (e.g. stateful APIs), generate sequences of operations,
  not just independent inputs
- End-to-end tests verify composition, not logic: run the full pipeline and assert
  system-level invariants. Keep them few, focused on the seams between components.
- Reserve example/unit tests for simple pure functions and for pinning regressions
  a stronger test uncovers.

### Performance

- Pre-allocate when size is known
- No allocations in hot paths
- Prefer worst-case over average-case algorithms
- No optimization without profiling data

### Determinism

When writing generators, output should be a pure function of (seed, config).

- Use explicit seed from config.
- Only iterate over ordered collections.
- No ambient inputs (wall-clock time, unsorted filesystem listings, ...).
- Don't let thread/task scheduling affect your outputs.
- Pin all serialization options (key order, separators, encoding, float precision)
  so the same data always serializes to the same bytes.

### Dependencies

- Evaluate before adding: determinism, control, criticality, performance, vs 
  maintenance/security risk and the long-term cost of owning a reimplementation.
- Default to a proven, well-maintained dependency for solved, non-core problems.
- Implement in-house only when a criterion genuinely fails and the surface is small
  enough to own, test, and verify.
- Upgrade policy is to pin to the major (breaking) boundary by default.
- Reproducibility comes from a committed lockfile for every deployable.
- Published libraries: avoid over-constraining consuming libraries by setting a
  low floor.
- Move dependencies into relevant groups when the language allows (e.g. dev, docs, test).

### Documentation

- Document why, not what. The code shows what; comments explain why.
- Use the language's documentation convention (doc comments / docstrings) at module
  level and on every public type and function.
- Describe functions in the imperative mood ("Send payload", not "Sends a payload").
  Document parameters, return value, and failure modes.
- ASCII-only preferred in code and documentation.

### Validation Workflow

- Validation commands should be defined by the task runner (e.g. make or just).
- If no command is provided, always run tools using the project configuration.
- Run validation after every code change.

| Task | Example Command |
|------|---------|
| Format | `just format` |
| Lint | `make check` |
| Test | `just test` |

## Key Reminders

1. Run validation after changes - never skip
2. Use project recipes when available, not raw commands.
3. Whenever making major code changes, make sure to update outdated documentation and tests.

## Review Checklist

When reviewing code:

- [ ] Tests added/updated for new functionality
- [ ] Error messages are actionable
- [ ] No hardcoded paths or credentials
- [ ] Documentation updated (README, docstrings, comment-based help)
- [ ] Backward compatibility maintained

---

*This file is optimized for both AI agents and human contributors. When in doubt, prioritize clarity and maintainability over cleverness.*
