# Annotated Example: Nix Flake Layout

A complete flake illustrating every convention the skill prescribes:
the root file, a per-component devenv shell, and a custom package
wrapper. Use it as the bootstrap template when starting from scratch.

## Layout

```
project-root/
└── tools/nix/
    ├── flake.nix
    ├── flake.lock
    ├── shells/
    │   └── data-pipeline.nix
    └── packages/
        └── treefmt.nix
```

## `flake.nix`

```nix
{
  description = "project devshell";

  nixConfig = {
    extra-substituters = [
      "https://nix-community.cachix.org"
      "https://devenv.cachix.org"
    ];
    extra-trusted-public-keys = [
      "nix-community.cachix.org-1:mB9FSh9qf2dCimDSUo8Zy7bkq5CX+/rkCWyvRCYg3Fs="
      "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw="
    ];
  };

  inputs = {
    nixpkgs.url     = "github:cachix/devenv-nixpkgs/rolling";
    flake-utils.url = "github:numtide/flake-utils";

    treefmt-nix = {
      url = "github:numtide/treefmt-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    devenv = {
      url = "github:cachix/devenv";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    { nixpkgs, flake-utils, devenv, ... }@inputs:
    let
      defineOutput =
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};

          packagesBasic = with pkgs; [
            git
            jq
            just
            kubectl
            (import ./packages/treefmt.nix { inherit inputs pkgs; })
          ];
        in
        {
          devShells = {
            default = pkgs.mkShell {
              packages = packagesBasic;
            };

            ci = pkgs.mkShell {
              packages = packagesBasic;
              shellHook = "unset TMPDIR";
            };

            data-pipeline = devenv.lib.mkShell {
              inherit pkgs inputs;
              modules = import ./shells/data-pipeline.nix { inherit pkgs; };
            };
          };
        };
    in
    flake-utils.lib.eachDefaultSystem defineOutput;
}
```

- **`nixConfig`** declares the cachix substituters and trusted keys
  for the nix-community and devenv caches. When the user opts in, builds
  pull pre-built artifacts instead of compiling from source.
- **`defineOutput`** is the per-system body. Keeping derivations inside
  this `let` block ensures `pkgs` and `packagesBasic` are recomputed for
  each target system.
- **`packagesBasic`** is the shared package list. Specialized shells
  extend it with `++`.
- **`data-pipeline`** uses `devenv.lib.mkShell` with modules pulled
  from `shells/data-pipeline.nix`; see `devenv-shells.md` for the
  module format.
- **`flake-utils.lib.eachDefaultSystem`** wraps the output for every
  supported system without duplicating the body.
