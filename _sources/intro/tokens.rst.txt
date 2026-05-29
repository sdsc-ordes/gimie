Token management
****************

Gimie requests data from third party APIs (Gitlab, Github) which require authentication to work. This authentication usually works with Personal Authentication Tokens (PATs). PATs are secret codes that can be used as passwords to perform actions on your behalf, but whose permissions can be limited to specific actions. Since Gimie only consumes data, it will normally work with tokens that have read-only permission.

Generating tokens can usually be done via the web interface of the service provider, and they must then be provided to Gimie. There are 2 ways to pass your token to Gimie:

1. Set the corresponding Environment variable. The token will only be accessible for the current session:


.. tab-set::

    .. tab-item:: Linux/Mac/BSD
        :selected:

        .. code-block:: console
            :emphasize-text: <repository-url>

            export GITLAB_TOKEN=<your-gitlab-token>
            export GITHUB_TOKEN=<your-github-token>

    .. tab-item:: Windows

        .. code-block:: console
            :emphasize-text: <repository-url>

            # You may need to restart windows after this
            setx GITLAB_TOKEN <your-gitlab-token>
            setx GITHUB_TOKEN <your-github-token>


2. Use a ``.env`` file in the current directory. Gimie will look for a file named ``.env`` and source it. The file contents should be as follows:

.. code-block::
    :emphasize-text: <repository-url>
    :caption: File: .env

    GITLAB_TOKEN=<your-gitlab-token>
    GITHUB_TOKEN=<your-github-token>


While the latter approach can be convenient to persist your token locally, it is generally not recommended to store your tokens in plain text as they are sensitive information. Hence the first approach should be preferred in most cases.

Encrypting tokens
=================

If you are serious about security, you should use a tool like `sops <https://github.com/mozilla/sops>`_ or `pass <https://www.passwordstore.org/>`_ to encrypt your secrets.

Below is a quick guide on how to use ``sops`` to store encrypted tokens, and decrypt them on the fly when using gimie.

.. dropdown:: Generating PGP key

    PGP is a public key encryption system. If you don't already have one, you will need to generate a key pair to encrypt your secrets.
    You can use the following command to generate a key pair. You will be prompted for a passphrase, but you may leave it empty if you wish.

    .. code-block:: bash

        gpg --gen-key

.. dropdown:: Set up SOPS

    SOPS needs to be configured to use your PGP key. You can do so by running the following command:
    Replace ``<FINGERPRINT>`` with the fingerprint of your PGP key (it looks like ``69AB B75E ...``). You can find it by running ``gpg --fingerprint``
    Upon running the command below, `sops` will open a `vim` buffer where you can enter the desired content of your .env file.
    Upon saving the file (``:wq``), ``sops`` will encrypt the file and save it as ``.enc.env``.

    .. code-block:: bash

        sops --pgp "${FINGERPRINT}" .enc.env

.. dropdown:: Source tokens

    Whenever you want to run gimie, you can decrypt secrets on the fly and pass them to gimie using the following command:

    .. code-block:: bash
        :emphasize-text: <repository-url>

        sops exec-env .enc.env 'gimie data <repository-url>'

    Or if you just want to inspect the decrypted file:

    .. code-block:: bash

        sops --decrypt .enc.env
