---
name: run-nix-devshell
description: >-
  Discovers and runs project tooling through a nix flake devshell. Triggers
  before running tools if the project contains a `flake.nix`, or when the
  user mentions `nix`. Wraps each command with `nix develop --command`.
  Skip for universal system tools (e.g. `git`, `cat`, `ls`, `grep`).
---

# Nix Devshell

## When To Use

Apply this skill whenever a project contains a `flake.nix` at the repo
root or under `tools/nix/`. The devshell provides the project's language
runtimes, linters, formatters, and CLIs; running tools without it risks
picking up the wrong version (or missing the tool entirely) from the base
system.

Local references in this skill:

- `references/nix-develop-cli.md` — `nix develop` invocation form and per-flag semantics.

## Step 1: Read `flake.nix`

Read the flake at the start of any task in a nix project:

```bash
cat flake.nix             # at the repo root
cat tools/nix/flake.nix   # under tools/
```

Look for:

- `devShells` — the names of available shells (e.g. `default`, `ci`).
- `packages` — the tools provided by each shell.
- `shellHook` — setup that runs on interactive shell entry (env vars,
  hook installs).


When the project contains a `justfile` and maybe a `nix.just` module declared as `mod nix '...'` in
the root justfile), look for a recipe wrapping `nix develop` with the project's standard flags.
Refer to the relevant skill for instructions on how to run the recipe.

## Step 2: Run Commands Through The Devshell

Prefer the just recipe when one exists; fall back to direct `nix develop`
otherwise. For example:

```bash
nix develop <flake-dir>#<shell> \
  --extra-experimental-features "flakes nix-command" \
  --accept-flake-config \
  --no-pure-eval \
  --command <cmd> [args...]
```

See `references/nix-develop-cli.md` for the meaning of each flag and when
to add or drop one.

### Picking The Shell

Use the shell from `devShells` that best fits the task — e.g. a
language- or component-specific shell when one exists. When no
shell clearly fits, use `default`.

### Examples

```bash
nix develop ./tools/nix#default \
  --extra-experimental-features "flakes nix-command" \
  --accept-flake-config --no-pure-eval \
  --command python ./script.py
```

## Operational Notes

- **`.envrc` does not apply to the agent.** direnv activates the
  devshell automatically in interactive terminals; the agent's shells
  do not source `.envrc`. Always invoke `nix develop --command` (or
  `just nix::develop`).
- **`shellHook` does not run under `--command`.** Hooks declared in
  `shellHook` only fire on interactive entry. When a recipe depends on
  an env var that `shellHook` would set, set it explicitly in the
  command or chain it inside `bash -c "export VAR=...; <cmd>"`.
- **`nix` not installed.** Stop and tell the user. Running commands
  outside the devshell may pick up missing or wrong-version tools and
  yield results that disagree with CI.
- **First run is slow.** A fresh checkout downloads and builds every
  flake input on the first `nix develop`; subsequent runs hit the cache.
  Warn the user before a long first run.
- **`devenv`-based shells** still enter through `nix develop`.
  `devenv.lib.mkShell` is a higher-level way to declare shell contents,
  not a different entry point.
