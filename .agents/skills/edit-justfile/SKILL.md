---
name: edit-justfile
description: >-
  Creates and edits `just` recipes for project automation. Triggers when
  adding, editing, or refactoring a `justfile`, `Justfile`, `.justfile`, or
  a `.just` module file. Encodes conventions for top-level settings, recipe
  layout, modules, naming, and secret handling. Skip when only running existing
  recipes — use the `run-just` skill instead.
---

# Edit Justfile

## When To Use

Apply this skill whenever creating or modifying a `justfile`, `Justfile`,
`.justfile`, or a `.just` module file. For invoking existing recipes, use
the `run-just` skill.

The official `just` manual is at <https://just.systems/man/en/>. Local
references in this skill:

- `references/just-features.md`: settings, attributes, modules, strings,
  dotenv, shebang semantics.
- `references/example-justfile.md`: a complete example layout.
- `references/modules.md`: module declaration, extraction rules, naming.
- `references/secrets.md`: `.env` layout and secret-touching recipe
  conventions.

## Step 1: Toplevel Baseline

Every justfile starts with the same baseline:

```just
set positional-arguments
set shell := ["bash", "-cue"]
set dotenv-load     # add only when the project uses a .env file

root_dir := `git rev-parse --show-toplevel`
```

Per-setting semantics live in `references/just-features.md` (Settings).
`root_dir` captures the git root so recipes can `cd {{root_dir}}` for paths
that must resolve from the project root.

## Step 2: Add The `[private] default` Recipe

The root justfile and every module file start with a `[private] default`
recipe that prints the recipe list:

```just
# Default recipe to list all recipes.
[private]
default:
    just --list
```

In a module file (e.g. `tools/just/build.just`), scope the listing to the
module:

```just
[private]
default:
    just --list build
```

This keeps `just` and `just <module>` helpful when called without arguments.

## Step 3: Write Recipes

Choose **linewise** when the body is one or two commands; choose **shebang**
when state must persist across lines.

### Linewise Recipes

```just
# Format the whole repository.
format *args:
    treefmt {{args}}
```

Each line runs in a fresh shell — chain with `&&` or switch to a shebang
recipe when state must persist. The comment above the recipe becomes its
documentation in `just --list`.

### Shebang Recipes

```just
# Build the project.
build target="release":
    #!/usr/bin/env bash
    set -euo pipefail
    cd {{root_dir}}/build
    for f in *.txt; do
      process "$f"
    done
```

Set strict mode inside the body — the recipe-level `set shell := [...]`
does not apply inside a shebang. See `references/just-features.md` (Shebang
Recipes) for the full semantics.

### Quoting

Quote `{{interpolations}}` whose value may contain spaces, paths, or shell
metacharacters. See `references/just-features.md` (Quoting Interpolations)
for examples.

### Destructive Recipes

Apply `[confirm]` to recipes that delete files, deploy services, push
images or releases, generate or rotate keys, or otherwise mutate state
outside the working tree.

```just
# Remove build artifacts.
[confirm("Remove build artifacts? [y/n]")]
clean:
    rm -rf "{{root_dir}}/build"
```

### Recipe Naming

Use short verbs for public recipes (`format`, `test`, `deploy`, `setup`),
more specific names for private helpers (`setup-commit-hooks`,
`render-helm`), and `<module>::<recipe>` for module recipes
(`image::build`, `nix::develop`).

## Step 4: Group Recipes Into Modules

When recipes cluster around a single domain, extract them into
`tools/just/<module>.just` and declare them with `mod` from the root
justfile. See `references/modules.md` for implementation conventions.

## Step 5: Handle Secrets

NEVER read, write, or modify files outside the project — including secret
files. Let the user manage them. If a secret value is read inadvertently,
inform the user explicitly and recommend they revoke it. This rule applies
regardless of whether the project handles secrets. See `references/secrets.md`
for secret management conventions.
