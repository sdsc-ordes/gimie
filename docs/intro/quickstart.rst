Quick start
***********

The easiest way to use gimie is to run it as a command line tool. Here's how to get started:

Install using pip or docker:

.. tab-set::

    .. tab-item:: pip
        :sync: pip
        :selected:

        .. code-block:: console

            pip install gimie

    .. tab-item:: docker
        :sync: docker

        .. code-block:: console

            docker pull ghcr.io/sdsc-ord/gimie:latest


.. warning::

    Before running gimie, you will need to obtain a personal access token for the GitHub and/or GitLab and export it as an environment variable. See :ref:`Token management` for more information.


Gimie can then be used as follows to extract repository metadata:

.. tab-set::

    .. tab-item:: pip
        :sync: pip
        :selected:

        .. code-block:: console
            :emphasize-text: <repository-url>

            gimie data <repository-url> > output.ttl

    .. tab-item:: docker
        :sync: docker

        .. code-block:: console
            :emphasize-text: <repository-url>

            docker run -e GITHUB_TOKEN=${GITHUB_TOKEN} ghcr.io/sdsc-ord/gimie:latest data <repository-url> > output.ttl


.. note::

    When running gimie in a container, you need to pass your github or gitlab token as an environment variable inside the container:
