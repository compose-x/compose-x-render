#!/usr/bin/env python

"""Tests for `compose_x_render` package."""

import pytest

from tempfile import TemporaryDirectory
from compose_x_render.compose_x_render import ComposeDefinition
from jsonschema.exceptions import ValidationError


from os import path

HERE = path.abspath(path.dirname(__file__))


def test_valid_input():
    test = ComposeDefinition([f"{HERE}/valid_input.yaml"])
    temp_dir = TemporaryDirectory()
    test.write_output(output_file=f"{temp_dir.name}/test.yaml")
    test.output_services_images(f"{temp_dir.name}/test.json")


def test_valid_extension_input():
    test = ComposeDefinition([f"{HERE}/valid_input.yaml", f"{HERE}/extension_input.yaml"])

    temp_dir = TemporaryDirectory()
    test.write_output(output_file=f"{temp_dir.name}/test.yaml", for_compose_x=True)


def test_invalid_extension_input():
    with pytest.raises(TypeError):
        test = ComposeDefinition([f"{HERE}/valid_input.yaml", f"{HERE}/invalid_extension.yaml"])


def test_fail_json_validation():
    with pytest.raises(ValidationError):
        test = ComposeDefinition([f"{HERE}/invalid_input.yaml"])


def test_invalid_ports_format():
    with pytest.raises(ValueError):
        test = ComposeDefinition([f"{HERE}/invalid_port_format.yaml"])
