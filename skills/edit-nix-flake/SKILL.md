---
name: edit-nix-flake
description: >-
  Creates and edits nix flakes that provide a project's devshells,
  packages, and tooling wrappers. Triggers when adding, editing, or
  refactoring a `flake.nix` or other `.nix` file. Encodes layout
  and architecture conventions. Skip when only running tooling through
  an existing devshell.
---

# Edit Nix Flake

## When To Use

Apply this skill whenever creating or modifying a `flake.nix`, a
`shells/*.nix` devenv module, or a per-package `.nix` file. For invoking
tooling through an existing devshell, use the `run-nix-devshell` skill.

References (load JiT): `references/example-flake.md` (annotated bootstrap),
`references/devenv-shells.md` (devenv modules), `references/packages.md` (wrapper derivations).

## Step 1: Choose The Layout

When starting from scratch, prefer placing all nix files under `tools/nix`.
If the project already uses a `flake.nix` at the root, only move it to `tools/nix`
when the complexity grows to warrant multiple files (devenv modules, package derivations).

```
project-root/
└── tools/nix/
    ├── flake.nix
    ├── flake.lock
    ├── shells/<name>.nix    # devenv modules, one per specialized shell
    └── packages/<name>.nix  # per-package derivations and wrappers
```

## Step 2: Set Up The Toplevel Structure

A `flake.nix` has four top-level attributes: `description`, `nixConfig`,
`inputs`, and `outputs`. Use `references/example-flake.md` as the
canonical skeleton when bootstrapping.

Decisions when adding inputs:

- Include `devenv` only when relevant (language-specific setups). Without
  devenv, use the latest stable nixpkgs (e.g.
  `nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05"`).
- `treefmt-nix` is the recommended formatter. See `references/packages.md`
  and the [official repository](https://github.com/numtide/treefmt-nix) for
  configuration.
- Pin sub-inputs with `inputs.X.inputs.nixpkgs.follows = "nixpkgs"` so the
  project's nixpkgs revision is reused and downloads are not duplicated.

## Step 3: Define A Devshell

Define the shared package list once in the `let` block, then extend it per
shell with `++`:

```nix
devShells.default = pkgs.mkShell {
  packages = packagesBasic ++ (with pkgs; [ kubectl kubernetes-helm ]);
};
devShells.ci = pkgs.mkShell {
  packages = packagesBasic;
  shellHook = "unset TMPDIR";
};
```

- **`default`** is the conventional name for the primary shell.
- Specialized shells (`ci`, `docs`, ...) sit alongside `default`.
- Sort packages alphabetically within each list to keep diffs minimal.

## Step 4: Component-Specific Shells With devenv

When a shell needs language-aware setup (Python+uv, Node+pnpm,
Rust+cargo), extract the configuration into `shells/<name>.nix` and load
it via `devenv.lib.mkShell`. See `references/devenv-shells.md` for the
module structure, the available language options, and when to prefer
devenv over plain `mkShell`.

## Step 5: Custom Packages And Wrappers

When a tool needs project-specific configuration (formatter rule sets,
patched derivations, CLI wrappers), define it in `packages/<name>.nix`
and import the resulting derivation into a package list. See
`references/packages.md` for the function signature and the treefmt
wrapper example.

## Operational Notes

- **ALWAYS** commit `flake.lock`. Treat it as source.
  Refresh it with `nix flake update` whenever modifying inputs.
- **ALWAYS** run `nix flake check` after editing nix files.
- `flake-utils.lib.eachDefaultSystem` covers the four
  common targets. Use `flake-utils.lib.eachSystem [ ... ]` when the
  project needs a narrower or wider set.
