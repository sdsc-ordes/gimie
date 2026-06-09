# devenv Module Shells

`devenv.lib.mkShell` accepts a list of modules that declare language
support, packages, and environment in a higher-level form than raw
`mkShell`. Use it when a shell needs language-aware tooling (Python+uv,
Node+pnpm, Rust+cargo).

## File Layout

Put the module definition in `shells/<component>.nix` and import it from
`flake.nix` via `devenv.lib.mkShell { inherit pkgs inputs; modules = import ./shells/<component>.nix { inherit pkgs; }; }`. See
`example-flake.md` for the import site in context.

## Module Structure

A module file returns a list of module attribute sets. Each module
declares some combination of `name`, `packages`, `env`, and language
toolchains:

```nix
# shells/data-pipeline.nix
{ pkgs, ... }: [
  {
    name = "data-pipeline";

    packages = [ pkgs.pyright pkgs.ruff ];

    env.UV_PROJECT = "src/pipeline";

    languages.python = {
      enable      = true;
      directory   = "src/pipeline";
      venv.enable = true;
      uv = {
        enable = true;
        sync = { enable = true; allExtras = true; };
      };
    };
  }
]
```

## Common Language Options

- **Python + uv**: `languages.python.enable`, `venv.enable`,
  `uv.enable`, `uv.sync.enable` to lock-sync on shell entry.
- **JavaScript / TypeScript**: `languages.javascript.enable` with
  `pnpm.enable`, `npm.enable`, or `yarn.enable`.
- **Rust**: `languages.rust.enable`, with `channel = "stable"` (or
  `nightly`).

See the [devenv options reference](https://devenv.sh/reference/options/)
for the full module surface.

## When To Use devenv Over `mkShell`

Use `devenv.lib.mkShell` when:

- The shell needs a virtualenv, lockfile sync, or other
  language-toolchain orchestration.
- Multiple environment variables and tools cluster around one
  component.

Use plain `mkShell` when the shell only needs a package list and at
most a one-line `shellHook`.
