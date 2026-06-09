# Handling Secrets In Justfiles

The standard practice is to keep secret values outside the repository
entirely and reference them by file path through `.env`. The hard
no-read/no-write rule for files outside the project tree is stated in
`SKILL.md` (Step 5) and applies regardless of the patterns below.

## `.env` Layout

Two paired files:

```sh
# .env.tpl  (tracked in git)
SERVICE_PASSWORD_FILE=

# .env       (gitignored)
SERVICE_PASSWORD_FILE=~/.config/service/secret.txt
```

- `.env.tpl` documents the variables a contributor needs to set. Track it.
- `.env` carries the real paths. Gitignore it.
- Source `.env` from the justfile via `set dotenv-load`.
- Store only file paths or non-sensitive configuration in `.env`; keep
  secret values in files outside the repository.

## Conventions For Secret-Touching Recipes

- Keep shell tracing off — DO NOT use `set -x` and `bash -x`.
- Pass values via stdin or process substitution (`--password-stdin`,
  `< "$FILE"`) rather than CLI arguments. CLI arguments are visible in
  `ps` output and shell history.
- Reference secret-bearing variables only where their value is consumed.
  Avoid `echo` and any interpolation into shell-traced commands.

These patterns keep secrets out of CI logs and `ps` output.

## Examples

**Good:**

```just
# Authenticate with the service.
login:
    service-cli login --user admin --password-stdin < "$SERVICE_PASSWORD_FILE"
```

**Bad:**

```just
# Authenticate with the service.
login:
    #!/usr/bin/env bash
    set -x   # prints the next line, including the secret value
    service-cli login --user admin \
      --password "$(cat $SERVICE_PASSWORD_FILE)"   # secret on CLI -> visible in `ps`
```
