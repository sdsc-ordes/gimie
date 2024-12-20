Notable changes introduced in gimie releases are documented in this file


## [0.7.2] - 2024-12-18

### Bug Fixes

- *(cff)* doi structure parsing (#121)


## [0.7.1] - 2024-12-09

### Bug Fixes

- *(dependency missing)* Added pyyaml (#119)


## [0.7.0] - 2024-11-28

### Bug Fixes

- *(cff)* enforce valid urls as doi (#108)- spelling mistake in run as library docs (#113)

### Documentation
- update gimie API examples (#105)
- add CFF file (#111)

### Features

- *(parser)* extract authors from CFF files (#115)- add parsers support (#97)
- cff to doi parser (#107)


## [0.6.0] - 2023-10-19

### Bug Fixes

- *(deps)* switch to scancode mini (#88)
- *(docker)* push action was missing buildx (#91)
- *(github)* replace superseded schema:isBasedOnUrl property (#80)- incorrect mapping for schema:codeRepository (#64)
- *(license)* NOASSERTION should not return triples. (#66)

### Features

- *(conventional-PRs)* all PRs will need to follow conventional format
- *(conventional-PRs)* all PRs will need to follow conventional format
- *(github.py)* Get "forked from" property of a repository (#79)
- *(io)* file-like interface to remote resources (#70)- license matcher for git extractor (#78)


## [0.5.1] - 2023-07-10

### Bug Fixes

- incorrect mapping for schema:codeRepository (#64)


## [0.5.0] - 2023-07-04

### Bug Fixes

- *(gitlab)* extraction of author on user-owned projects (#57)

### Documentation

- add docs website (#58)

### Features

- *(gitlab)* support private instances (#62)


## [0.4.0] - 2023-06-09

### Bug Fixes

- *(docs)* execute Makefile rule with poetry
- *(gitlab)* edge case where no release available
- *(gitlab)* pass user node to _get_author instead of parent node
- *(gitlab)* rm debug breakpoint
- *(gitlab)* extraction of author on user-owned projects (#57)- gitlab download url
- prevent license finder from picking up docs files

### Documentation

- *(api)* reduce autodoc ToC depth
- *(cli)* add and configure sphinx-click to work with typer
- *(deps)* introduce doc dependency group
- *(git)* rm duplicate attibute from docstring
- *(setup)* add sphinx configuration
- *(style)* add logo + favicon
- *(style)* add logo to front page
- *(theme)* furo -> sphinxawesome
- *(theme)* add sphinx_design extension, downgrade to sphinx6 for compat
- *(tokens)* Add tutorial for encrypted tokens
- *(tokens)* fix windows instructions- add Makefile rule to generate sphinx website
- initial sphinx website with apidoc
- add apidoc output to gitignore
- add intro pages
- improve header names
- add quickstart section, enable tabbing and crossref
- add sphinx-tabs as doc dep
- add sphinx-copybutton extension
- add changelog and configure git-cliff
- replace deprecated commonmark parser with myst
- enable placeholder highlighting extension
- improve index format
- add windows variant for env var
- add docs website (#58)
- update readme and add docs badge

### Features

- *(gitlab)* fallback to rest api if author missing from graphql. make type hints py38 compat.
- *(io)* Allow rdflib kwargs in serialize()- use GraphQL API in gh extractor (#33)
- Git extractor (#42)
- disallow local paths (#46)


## [0.3.0] - 2023-02-24

### Bug Fixes

- exclude hidden files from license search
- correctly handle one or multiple license paths
- temporarily disable scancode (#19)
- rename GITHUB_TOKEN to ACCESS_TOKEN
- change token back to ACCESS_TOKEN since GITHUB_TOKEN failed
- GITHUB_TOKEN must be prefixed with github as environment variable
- set test workflow back to using ACCESS_TOKEN as a repo secret
- add .dockerignore, copy necessary files only and improve comments
- rename container-publish.yml into docker-publish.yml
- 'building docker image' instead of 'building docker container'

### Documentation

- define initial contributing guidelines
- add usage examples in README
- update copyright notice in license
- specify type hints and rm unused imports in LicenseMetadata
- add dev status in readme
- document the release process in the readme
- readme badges (#25)
- add section to the readme on how to provide a github token
- adapt documentation to usage of ACCESS_TOKEN instead of GITHUB_TOKEN
- adapt readme to installation with makefile
- give options to install either PyPI or dev version of gimie
- add message for docker-build Makefile rule
- add image annotations to dockerfile
- add docker instructions in readme

### Features

- *(cli)* add CLI skeleton (#9)- initial project definition with pyproject.toml
- add placeholder folders
- add placeholder tests
- add basic repo class and placeholder source interfaces
- add console entrypoint definition in pyproject.toml
- add GitMetadata methods to get commit authors and repository creation date
- add method to get releases date and commit hash
- sort releases by date
- add method to get git repo creator
- add unit tests for git source
- Created a license finder using scancode toolkit
- Added triple serialization of license result (spdx url)
- use cached property from functools
- added a make_graph script. Now only contains add_license_to_graph().
- Created software class, and make graph functions, black reformat
- add license scanner (#12)
- add prototype for RDF graph serialization (#15)
- initial architecture with GithubExtractor (#23)
- add python-dotenv to dependecies
- pick up github token from the environment variables
- add `.env.dist` file as an example for a `.env` file
- provide option to provide github_token when calling extractor
- add pre-commit to dependencies
- add makefile to make installation easier
- add Dockerfile and entrypoint.sh
- add Makefile rule to build the docker image
- add github workflow to push image to github container registry


<!--generated by git-cliff -->
