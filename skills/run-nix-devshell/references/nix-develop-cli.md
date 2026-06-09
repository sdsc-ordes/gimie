# `nix develop` CLI Reference

Reference for invoking `nix develop` non-interactively to run a single
command inside a flake's devshell.

## Invocation

```bash
nix develop <flake-dir>#<shell> [flags] --command <cmd> [args...]
```

- `<flake-dir>` — path to the directory containing `flake.nix` (e.g. `.`
  for the repo root, `./tools/nix` for a nested flake).
- `<shell>` — the name of a devshell from `devShells` (e.g. `default`,
  `ci`, `docs`).
- `--command <cmd> [args...]` — run the command inside the shell and
  exit, instead of opening an interactive prompt. Omit to enter the
  shell interactively (rarely needed by the agent).

## Common Flags

| Flag                                                | When to include                                                                                  |
|-----------------------------------------------------|--------------------------------------------------------------------------------------------------|
| `--extra-experimental-features "flakes nix-command"` | When the system `nix.conf` does not already enable flakes. Safe to include unconditionally.      |
| `--accept-flake-config`                             | When the flake declares a `nixConfig` block with custom substituters or trusted public keys. Without it, nix prompts interactively. |
| `--no-pure-eval`                                    | When the flake reads from the filesystem outside its own tree (e.g. `import ./../something.nix`). |
| `--impure`                                          | When the flake reads environment variables at evaluation time. Stronger than `--no-pure-eval`.   |
| `--refresh`                                         | When the flake's inputs need to be re-resolved from upstream. Slow; reserve for explicit refresh requests. |

The first three flags match what `.envrc` and `just nix::develop` typically
pass. Mirror that set when calling `nix develop` directly so the behaviour
stays consistent across entry points.

## Mapping `nix develop` Output To The Source

When a command fails inside the devshell, the failure reflects the tool's
own behaviour, not the devshell. Read the tool's output first; only treat
the failure as a devshell issue when:

- the tool is reported as not found (devshell missing a package, wrong
  shell selected),
- an environment variable expected by the tool is unset (likely a
  `shellHook` that did not run — see SKILL.md "Operational Notes").
