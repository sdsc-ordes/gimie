Token management
****************

Gimie requests data from third party APIs (Gitlab, Github) which require authentication to work. This authentication usually works with Personal Authentication Tokens (PATs). PATs are secret codes that can be used as passwords to perform actions on your behalf, but whose permissions can be limited to specific actions. Since Gimie only consumes data, it will normally work with tokens that have read-only permission.

Generating tokens can usually be done via the web interface of the service provider, and they must then be provided to Gimie. There are 2 ways to pass your token to Gimie:

1. Set the corresponding Environment variable. The token will only be accessible for the current session:

.. code-block::

   export GITLAB_TOKEN=<your-gitlab-token>
   export GITHUB_TOKEN=<your-github-token>

2. Use a ``.env`` file in the current directory. Gimie will look for a file named ``.env`` and source it. The file contents should be as follows:

.. code-block::

   GITLAB_TOKEN=<your-gitlab-token>
   GITHUB_TOKEN=<your-github-token>


While the latter approach can be convenient to persist your token locally, it is generally not recommended to store your tokens in plain text as they are sensitive information. Hence the first approach should be preferred in most cases.
