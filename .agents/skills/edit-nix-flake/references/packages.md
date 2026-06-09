# Custom Packages And Wrappers

When a tool needs project-specific configuration (formatter rule set,
patched derivation, CLI wrapper), define it in `packages/<name>.nix`
and import the resulting derivation into a flake package list.

## File Layout

Put the wrapper in `packages/<name>.nix` and add
`(import ./packages/<name>.nix { inherit inputs pkgs; })` to a package
list in `flake.nix`. See `example-flake.md` for the import site in
context.

## Function Signature

A package file is a function taking the inputs it needs and returning a
single derivation:

```nix
{ inputs, pkgs, ... }:
let
  # derivation construction
in
  derivation
```

Accept only the arguments the file actually uses — `pkgs` for plain
nixpkgs derivations, `inputs` for sub-inputs (treefmt-nix, devenv,
custom flakes).

## Treefmt Wrapper Example

```nix
# packages/treefmt.nix
{ inputs, pkgs, ... }:
let
  treefmtEval = inputs.treefmt-nix.lib.evalModule pkgs {
    projectRootFile = ".git/config";

    settings.global.excludes = [ "external/*" ];

    programs.prettier.enable = true;
    programs.ruff.enable     = true;
    programs.nixfmt.enable   = true;
    programs.shfmt = {
      enable      = true;
      indent_size = 4;
    };
  };
in
treefmtEval.config.build.wrapper
```

- **`projectRootFile`** tells treefmt where the project root is;
  `.git/config` is the conventional sentinel.
- **`settings.global.excludes`** paths are relative to the project root.
- Each **`programs.<formatter>`** block enables and configures one
  formatter; see the
  [treefmt-nix programs list](https://github.com/numtide/treefmt-nix/tree/main/programs)
  for available formatters and their options.
- **`treefmtEval.config.build.wrapper`** is a single derivation that
  bundles every enabled formatter behind one `treefmt` executable.
