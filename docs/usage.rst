.. meta::
    :description: Compose-X Render usage examples
    :keywords: Compose-X, Compose, docker-compose

=====
Usage
=====

To use Compose-X Render in a project

.. code-block:: python

    from compose_x_render.compose_x_render import ComposeDefinition

    compose_content = ComposeDefinition(["/path/to/file.yaml", "/path/to/file2.yaml"])
    print(compose_content.definition)


