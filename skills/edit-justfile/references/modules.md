# Modules

A module is a separate `.just` file declared from the root justfile.
Module recipes are invoked as `<module>::<recipe>` and live in their own
namespace with their own settings and variables.

## Declaration

Declare modules at the bottom of the root justfile, clustered under one
group:

```just
# Manage OCI images.
[group('modules')]
mod image 'tools/just/image.just'

# Manage external dependencies.
[group('modules')]
mod external 'tools/just/external.just'
```

`[group('modules')]` clusters module declarations under one header in
`just --list`, so they stay together in the listing rather than mingling
with public recipes.

A module file is itself a complete justfile (settings, `[private] default`,
recipes). See `example-justfile.md` for the full pattern.

## When To Extract A Module

Extract a module when recipes share a domain and benefit from their own
namespace:

- Multiple recipes touch the same subsystem (`image::build`, `image::push`,
  `image::scan`).
- The recipes share module-local variables (registry, platforms, tag
  defaults).
- The domain is independently usable — a contributor working on a
  different subsystem doesn't need to read these recipes.

Keep recipes in the root justfile when they:

- Stand alone (a single `clean` or `format`).
- Only compose module recipes
  (`deploy: just image::build && just image::push`).
- Belong to no clear domain.

## Naming

Name modules after the functionality they manage, not the tool they use
(`image` over `docker`, `external` over `vendir`). The tool is an
implementation detail that may change; the domain rarely does.
