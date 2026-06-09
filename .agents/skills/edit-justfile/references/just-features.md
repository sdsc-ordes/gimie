# Just Feature Reference

Condensed reference for the `just` features used in this skill. Consult the
official manual at <https://just.systems/man/en/> for anything this
reference omits.

## Settings (`set`)

| Setting                            | Purpose                                                                                       |
|------------------------------------|-----------------------------------------------------------------------------------------------|
| `set shell := ["bash", "-cue"]`    | Default shell for linewise recipes. `-c` reads command; `-u` errors on unset vars; `-e` exits on error. |
| `set positional-arguments`         | Pass recipe args as `$1`, `$2`, `$@` in addition to `{{var}}`. Required for shebang recipes that re-emit args. |
| `set dotenv-load`                  | Source `.env` from the project root into the shell environment of every recipe.               |
| `set dotenv-filename := "name"`    | Override the dotenv file name (default `.env`).                                               |
| `set dotenv-path := "path"`        | Override the dotenv search path.                                                              |
| `set dotenv-required`              | Fail loudly when the dotenv file is missing instead of silently degrading.                    |
| `set export`                       | Export every just variable into the recipe environment.                                       |
| `set fallback`                     | Search parent directories for a justfile when none is found in the current directory.         |
| `set allow-duplicate-recipes`      | Permit later definitions to override earlier ones; prefer unique recipe names so the override is not silent. |
| `set ignore-comments`              | Strip `#` lines from recipe bodies before execution.                                          |

Each setting may appear at most once. Settings cannot use backticks or
function calls.

## Recipe Attributes

| Attribute                           | Purpose                                                                                  |
|-------------------------------------|------------------------------------------------------------------------------------------|
| `[private]`                         | Hide from `just --list`. Use for helpers called by other recipes.                        |
| `[confirm]`                         | Prompt `y/n` before running. Apply to destructive recipes.                               |
| `[confirm("prompt text")]`          | Same, with a custom prompt.                                                              |
| `[group('name')]`                   | Group recipes under a header in `just --list`. Apply `[group('modules')]` to `mod` lines to cluster module declarations. |
| `[no-cd]`                           | Run the recipe in the caller's `cwd` instead of the justfile directory.                  |
| `[working-directory("path")]`       | Run the recipe in a specific path.                                                       |
| `[doc("text")]`                     | Set the documentation shown in `just --list` (overrides the preceding `#` comment).      |
| `[unix]` / `[linux]` / `[macos]` / `[windows]` | Restrict the recipe to a specific platform.                                   |
| `[no-exit-message]`                 | Suppress the `error: Recipe failed` footer on failure.                                   |
| `[script]`                          | Run the body as a script via `script-interpreter`, similar to a shebang recipe.          |

Multiple attributes may be comma-separated on one line:
`[private, confirm("...")]`.

## Variables

```just
name := "value"                              # plain assignment
root_dir := `git rev-parse --show-toplevel`  # backtick: shell command stdout
home := env('HOME')                          # environment variable; errors if absent
shell := env('SHELL', 'bash')                # environment variable with default
export RUST_BACKTRACE := "1"                 # exported to recipe environments
```

Command-line override: `just name=value <recipe>` or `just --set name value <recipe>`.

Inside recipe bodies, reference variables with `{{name}}`. Just variables and
recipe parameters are *not* exported to backtick substitutions in the same
scope; use `set export` to expose them.

## Modules

```just
mod image                          # loads ./image.just or ./image/mod.just
mod image 'tools/just/image.just'  # explicit path
```

Call module recipes with `::`:

```bash
just image::build    # invoke the `build` recipe of the image module
just --list image    # list recipes inside the image module
```

Override a module's variables on the command line:

```bash
just image::tag=v2 image::build
just --set image::tag v2 image::build
```

Modules vs `import`: a module is a separate namespace with its own recipes
and settings; `import` inlines another file into the current namespace.
Prefer modules so recipes stay grouped by domain.

## Strings

| Form                      | Behavior                                                              |
|---------------------------|-----------------------------------------------------------------------|
| `'literal'`               | Single-quoted: no escapes; backslashes are literal.                   |
| `"with \n escapes"`       | Double-quoted: standard escape sequences (`\n`, `\t`, `\\`, `\u{…}`). |
| `'''triple literal'''`    | Multi-line literal, dedented.                                         |
| `"""triple escaped"""`    | Multi-line with escapes, dedented.                                    |
| `` `cmd` ``               | Backtick: shell command, captured stdout becomes the value.           |

Inside a recipe body, write `{{{{` to emit a literal `{{`.

## Quoting Interpolations

Quote `{{interpolations}}` whose value may contain spaces, paths, or shell
metacharacters:

```just
# Good: cp sees two arguments even when {{src}} contains a space.
copy src dest:
    cp -r "{{src}}" "{{dest}}"

# Pitfall: unquoted interpolation splits on whitespace.
copy src dest:
    cp -r {{src}} {{dest}}
```

## Argument Forwarding

```just
recipe-a arg:               # one required positional
recipe-b arg="default":     # one with default
recipe-c *args:             # zero or more, space-separated
recipe-d +args:             # one or more, space-separated
recipe-e a b *rest:         # mixed
```

Call: `just recipe-c a b c` → `{{args}}` becomes `a b c`.

`set positional-arguments` additionally exposes args as `$1`, `$2`, `$@`,
which matters in shebang recipes that re-emit arguments to another command.

## Dotenv Loading

`set dotenv-load` reads `.env` from the project root. The variables enter the
*shell environment* of the recipe, not the just variable namespace:

- Reference dotenv variables as `$DATABASE_URL` (or `${DATABASE_URL}`) in
  the shell. `{{DATABASE_URL}}` would resolve to a just variable instead.

Combine with `set dotenv-required` to fail loudly when `.env` is missing
rather than silently degrading.

## Shebang Recipes

```just
build:
  #!/usr/bin/env bash
  set -euo pipefail
  cd {{root_dir}}/build
  for f in *.txt; do
    process "$f"
  done
```

- The shebang line is the first line of the recipe body, indented like the
  rest of the recipe.
- The whole body runs in a single interpreter process, so multi-line state
  (loops, variables, `cd`) persists across lines.
- The recipe-level `set shell := [...]` does *not* apply: the shebang
  defines its own interpreter and flags.
- Set strict mode explicitly inside the body (`set -euo pipefail` for bash;
  the equivalent for other interpreters).
- Reserve `#!/usr/bin/env -S bash -euo pipefail` for cases that require
  kernel-level flag handling (rare).

Choose linewise recipes when the body is one or two commands; choose shebang
recipes when state must persist across lines.
