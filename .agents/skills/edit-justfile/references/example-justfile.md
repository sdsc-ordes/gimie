# Annotated Example: Justfile Layout

A minimal layout illustrating every convention the skill prescribes: the
root justfile plus one module.

## Layout

```
project-root/
├── justfile
├── .env             # gitignored
├── .env.tpl         # tracked template
└── tools/just/
    └── build.just
```

## Root `justfile`

```just
set positional-arguments
set shell := ["bash", "-cue"]

root_dir := `git rev-parse --show-toplevel`

# Default recipe to list all recipes.
[private]
default:
    just --list

# Format the whole repository.
format *args:
    treefmt {{args}}

# Remove build artifacts.
[confirm("Remove build artifacts? [y/n]")]
clean:
    rm -rf "{{root_dir}}/build"

# Run the full release pipeline.
release: format
    just build::compile
    just build::package

# Manage build artifacts.
[group('modules')]
mod build 'tools/just/build.just'
```

- `clean` wraps a state-mutating operation with `[confirm("...")]`.
- `release` composes a workflow from module recipes rather than
  reimplementing them.
- `mod` lives at the bottom under `[group('modules')]`.

## Module File `tools/just/build.just`

```just
set positional-arguments
set shell := ["bash", "-cue"]
root_dir := `git rev-parse --show-toplevel`

target := "release"

# Default recipe to list all recipes in this module.
[private]
default:
    just --list build

# Compile the project.
compile *args:
    cargo build --{{target}} {{args}}

# Package compiled binaries into tarballs.
package version="latest":
    #!/usr/bin/env bash
    set -euo pipefail
    cd {{root_dir}}/target/{{target}}
    for bin in *; do
      tar -czf "{{root_dir}}/dist/${bin}-{{version}}.tar.gz" "${bin}"
    done
```

- `target` is a module-local variable, overridable from the command line
  with `just build::target=debug build::compile`.
- `compile` is linewise: a single command suffices.
- `package` is a shebang recipe because `cd` and the loop must share one
  shell. `set -euo pipefail` provides strict mode inside the shebang body
  (the recipe-level `set shell` does not apply there).
- `*args` (variadic) and `version="latest"` (default) show the two common
  parameter forms.
