================
Compose-X Render
================

-------------------------------------------------------------------------------
Library & Tool to compile/merge compose files with top level extension fields
-------------------------------------------------------------------------------

Usage
=======

.. code-block:: bash

    usage: compose-x-render [-h] -f COMPOSEFILES [-o OUTPUT_FILE] [-x] [_ [_ ...]]

    positional arguments:
      _

    optional arguments:
      -h, --help            show this help message and exit
      -f COMPOSEFILES, --docker-compose-file COMPOSEFILES
                            Path to the Docker compose file
      -o OUTPUT_FILE, --output-file OUTPUT_FILE
                            Output directory to write all the templates to.
      -x, --compose-x-macro
                            Auto-Format for ECS Compose-X CFN Macro


Examples
=========

.. code-block:: bash

    # Simply merge two files and render into a 3rd
    compose-x-render -f docker-compose.yaml -f envs/aws.yaml -o aws.yaml

    # Merge two files and render in a ECS Compose-X Format for CFN Macro
    compose-x-render -x -f docker-compose.yaml -f envs/aws-prod.yml -o aws-prod.yaml


Why use compose_x_render ?
===========================

When using `docker-compose`_ you can merge multiple docker-compose files together which are going to override or add settings
from one definition file to the next one (with the last one having the highest priority in override).

Whilst `docker-compose`_ **config** execution is very useful to validate the definition of a file against a given revision,
the top level extensions files, marked with **x-** (i.e. *x-my_config*) get removed whilst the ones set at the services level
are left intact.

Docker Compose also does not offer a particular API in order to re-use the same validator and merge process.


Compose-X Render aims to bridge that gap, by providing both the CLI option for people to merge multiple config files with top level
x-extension fields, and simply provide them with ability to provide an API input to read files, and provide the merged YAML content.

If you happen to use `ECS Compose-X`_ (off which this sub-library was created) you can render your compose files that you plan to use with
the AWS CloudFormation Macro for Compose-X which allows you use it from within AWS and no CLI.


Features
========

* Allows to assemble multiple docker-compose definitions together
* Allows to preserve top-level x-fields
* For use with ECS Compose-X specifically, allows to automatically generate the final ComposeFile and use the CFN macro for it.

Docker compose definitions support

* 3.7
* 3.8
* 3.9


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _docker-compose: https://docs.docker.com/compose/
.. _ECS Compose-X: https://github.com/compose-x/ecs_composex
