Git repositories
****************

Software projects are usually versioned controlled and hosted on a server. Git is by far the most popular version control system, and is commonly used for scientific software and data science projects.

Git natively stores some metadata about the project authors and contributions in a local index, but git providers (servers) such has Github and GitLab store and expose more advanced information about the project and contributors. These information are served in provider-dependent format with specific APIs.

Gimie aims to provide provider-agnostic metadata in an interoperable format. It will request data from the provider API if available, or from git by cloning the repository into a temporary folder otherwise. This metadata is then converted to the widely used schema.org standard so that it can readily be integrated with other tools and services.
