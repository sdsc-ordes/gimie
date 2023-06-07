Quick start
***********

The easiest way to use gimie is to run it as a command line tool. Here's how to get started:

Install using pip or docker:

.. tabs::

    .. tab:: pip

        .. code-block::

            pip install gimie

   .. tab:: docker

        .. code-block::

            docker pull ghcr.io/sdsc-ord/gimie:latest



Before running gimie, you will need to obtain a personal access token for the GitHub and/or GitLab and export it as an environment variable. See :ref:`Token management` for more information.

Gimie can then be used as follows to extract repository metadata:

.. code-block:: console

    gimie data <repository-url> > output.ttl

If running gimie in a container, you would have to pass your github or gitlab token as an environment variable inside the container:


.. code-block:: console

    docker run -e GITHUB_TOKEN=${GITHUB_TOKEN} ghcr.io/sdsc-ord/gimie:latest data <repository-url> > output.ttl
