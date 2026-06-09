
# Adding New Skills

## Choose A Suitable Location

Skills can technically live anywhere, but should generally be kept in
standardized locations for discoverability and compatibility with supporting
tooling such as setup scripts.

## Set Up The Directory Structure

Every skill must follow this directory structure:

```
skill-name/
├── SKILL.md              # Required: Metadata + core instructions (<500 lines)
├── scripts/              # Executable code (Python/Bash) designed as tiny CLIs
├── references/           # Supplementary context (schemas, cheatsheets)
└── assets/               # Templates or static files used in output
```

- **SKILL.md**: Entry point for the skill. Should be kept relatively short, but
  can reference other resources for the agent to load when relevant.
- **References**: Additional context that is linked directly from SKILL.md. Keep
  them one level deep only, i.e. don’t create any subdirectories under this
  directory.
- **Scripts**: Use for fragile/repetitive operations where variation is a bug.
  Do not bundle library code here; long-lived library code belongs in standard
  repo CLI directories.

### Set Up SKILL.md

The SKILL.md file is made up of two components: the frontmatter, which is
written in YAML, and the body, which is written in Markdown. The frontmatter is
always loaded by the agent and contains the information it uses to decide when
to lazily load the body of the rest of the skill. The body is the initial
content loaded by the agent when the skill is loaded, although the agent may
choose to load additional context referred to by the body.

The frontmatter is separated by a starting and ending --- on their own lines,
resulting in file content that looks along the lines of

```
---
name: cl-description
description: >-
  Use this skill to draft, write, or format a Changelist (CL) description or
  commit message strictly following SDSC guidelines.
---
<Arbitrary Markdown content>
```

The name and description in the frontmatter of your SKILL.md are the only fields
that the agent sees before triggering a skill and are subject to several
restrictions.

- **Strict Naming**: The name field must be 1-64 characters, contain only
  lowercase letters, numbers, and hyphens (no consecutive hyphens), and must
  exactly match the parent directory name (e.g., name: wiz-testing must live in
  wiz-testing/SKILL.md).
- **Trigger-Optimized Descriptions**: (Max 1,024 characters). Describe the
  capability in the third person and include specific triggers and “negative
  triggers”. Cannot contain XML tags.
  - Bad: “Wiz skills.” (Too vague).
  - Good: “Creates and builds Wiz components using external Sass. Use when the
    user wants to update component styles or build configurations. Don't use it
    for external Sass styles with other frameworks.”

