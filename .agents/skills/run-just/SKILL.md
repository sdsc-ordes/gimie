---
name: run-just
description: >-
  Discovers and runs `just` recipes for operations such as build, test,
  lint, format or deploy. Triggers on operational tasks inside a repository,
  even when the user does not mention `just` explicitly. Prefers existing
  recipes over raw commands like `docker compose up`, `uv run`, or `nix develop`.
  Use only when the project contains a `justfile`, `Justfile`, or `.justfile`.
---

# Just Command Runner

## When To Use

Apply this skill before running any command for an operational task in a
project directory: build, test, lint, format, serve, deploy, or starting a
dev shell. Check for a project recipe before reaching for raw tooling such
as `docker compose up`, `uv run`, or `ruff check`.

## Step 1: Read The Justfile Source

From the git root, read the root `justfile` directly:

```bash
cat justfile
```

When the root file is absent, also check for `Justfile` (capital J) or
`.justfile`. When none exist, or when `just` is not installed, proceed with
direct commands and stop here.

Reading the source reveals:

- Recipe names and argument signatures, including defaults and variadic args.
- Comments documenting recipe intent.
- `mod` declarations pointing to module files, for example
  `mod compose 'tools/just/compose.just'`.

Read a module's source file directly before invoking any of its recipes, so
the arguments, defaults, and effects are clear in advance.

## Step 2: Match The Task To A Recipe

Map the user's task to the closest matching recipe. Prefer an exact recipe
match over an equivalent raw command. Examples:

| Task            | Prefer         | Over                        |
|-----------------|----------------|-----------------------------|
| Run tests       | `just test`    | `bash ./tests/test_flow.sh` |
| Format code     | `just format`  | `treefmt`                   |
| Lint code       | `just lint`    | `ruff check`                |
| Start dev shell | `just develop` | `nix develop`               |
| Deploy stack    | `just deploy`  | `docker compose up`         |

When no recipe matches, fall back to direct commands.

## Step 3: Run The Recipe

```bash
just <recipe> [args]
just <module>::<recipe> [args]
```

Most recipes use `set shell := ["bash", "-cue"]` and exit immediately on error.
When a recipe fails, consult the source already read in Step 1 to identify the
cause before retrying.

### Argument Signatures

Signatures are visible in the source from Step 1:

```just
format *args:        # variadic
test:                # no arguments
build target="all":  # default argument
```

### Confirm Before Running Destructive Recipes

Treat a recipe as destructive when it modifies state outside the working copy:

- **Deploys or starts services**: brings up infrastructure or application stacks.
- **Stops or destroys**: tears down services or removes data.
- **Cryptographic material**: generates, encrypts, or decrypts keys or secrets.
- **Publishes**: pushes images, packages, or releases. Any recipe whose name
  contains `push` or `publish` qualifies.

State the exact command and wait for user confirmation before running a
destructive recipe. When the user has already requested the operation
explicitly (for example "deploy the stack"), treat that request as
confirmation.

Never directly read decrypted secret files.

## Operational Notes

- **Run from the git root.** Many justfiles set
  ``root_dir := `git rev-parse --show-toplevel` `` and `cd {{root_dir}}` inside
  recipes. Invoking `just` from the git root ensures the justfile is found.
- **`set dotenv-load`** automatically sources `.env` from the project root,
  making variables in `.env` available to recipes without manual export.
- **Call only public recipes.** Recipes annotated `[private]` are internal
  helpers (for example `pick`, `cmd`, `require-enc-prefix`); they are hidden
  from `just --list` and intended for use by other recipes. Use the public
  recipes that wrap them.
- **Module `default` recipes list the module's recipes.** Running
  `just compose` prints the list of compose recipes; pick a specific recipe to
  execute something.

## Modules

When the root justfile declares a module such as `compose` or
`secrets` (look for the matching `mod` line), inspect the rules in
the module file to discover its recipes.

## Override variables

For details and examples on how to manually set variables from the command line, see [override-variables](./references/override-variables.md).

