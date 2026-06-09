# agents

This repository contains agent guidelines for sdsc-ordes repositories.
It is meant as a shared knowledge base for AI agents such that they follow our standard practices.

## Structure

```
AGENTS.md # Basic agent behavior.
ai-usage/ # AI policy [for humans].
skills/   # Task-specific instructions.
hooks/    # Event-triggered scripts. [TODO]
```

## Usage

Files in this repository should be imported into your repositories.
This repository is likely to evolve, thus we recommend using a dynamic import mechanism.

Here are example solutions:

### Gitignored Clone

Clone into your repository, and gitignore the subdirectory.

> [!NOTE]
> This assume you have github configured as an ssh host.

```bash
# Clone this repo under .agents/
$ git clone git@github.com:sdsc-ordes/agents .agents

# Redirect your root AGENTS.md/CLAUDE.md to this one.
$ echo "@.agents/AGENTS.md" > AGENTS.md
$ ln -s AGENTS.md CLAUDE.md

# Gitignore all guidelines
cat >> .gitignore <<EOF
.agents/
AGENTS.md
CLAUDE.md
EOF
```

### Declarative vendir Configuration

Include only specific files from the repo through a config file.

```bash
# Only include skills/ directory into .agents/skills/
$ mkdir -p tools/vendir/ .agents/
$ cat >> tools/vendir/vendir.yml <<EOF
apiVersion: vendir.k14s.io/v1alpha1
kind: Config
directories:
  - path: .agents/skills
    contents:
      - path: .
        git:
          url: https://github.com/sdsc-ordes/agents
          ref: main
        newRootPath: skills/
EOF

# Pull latest version matching the ref (`main`)
$ vendir sync --chdir tools/vendir/

# Pull exact reference from lockfile
$ vendir sync --locked --chdir tools/vendir/
```

### Check in with `git subtree`

With this approach, this repository will be available as a subdirectory in your project, and you can always update to the latest version.
Contributors don't need to be aware of the subtree (unlike submodules).

```bash
# Add repo in .agents/, with the history squashed into a single commit
$ git remote add -f sdsc-agents github.com:sdsc-ordes/agents
$ git subtree add --prefix=.agents/ sdsc-agents main --squash

# Pull remote updates to local subtree
$ git subtree pull --prefix=.agents/ sdsc-agents main --squash
```


## Credits

`AGENTS.md` is inspired by [DataDog/lading](https://github.com/DataDog/lading).
