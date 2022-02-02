#!/usr/bin/env python

"""Tests for `compose_x_render` package."""

from unittest import mock
import os
import pytest

from tempfile import TemporaryDirectory
from compose_x_render.compose_x_render import ComposeDefinition
from compose_x_render.networking import PORTS_STR_RE
from compose_x_render.envsubst import expandvars
from jsonschema.exceptions import ValidationError


from os import path

HERE = path.abspath(path.dirname(__file__))


@pytest.fixture(autouse=True)
def mock_settings_env_vars():
    with mock.patch.dict(os.environ, {"TESTING_EXISTS": "ROUGE"}):
        yield


def test_envsubst_inexistant(mock_settings_env_vars):
    assert expandvars("$SHELL") is not None
    assert expandvars("${TOTO:-default}") == "default"
    assert expandvars("${TESTING_EXISTS:-default}") == "ROUGE"
    assert expandvars("${TESTING_EXISTS:+override}") == "override"


def test_valid_input():
    test = ComposeDefinition([f"{HERE}/valid_input.yaml"])
    temp_dir = TemporaryDirectory()
    test.write_output(output_file=f"{temp_dir.name}/test.yaml")
    test.output_services_images(f"{temp_dir.name}/test.json")


def test_valid_extension_input():
    test = ComposeDefinition(
        [f"{HERE}/valid_input.yaml", f"{HERE}/extension_input.yaml"]
    )

    temp_dir = TemporaryDirectory()
    test.write_output(output_file=f"{temp_dir.name}/test.yaml", for_compose_x=True)


def test_invalid_extension_input():
    with pytest.raises(TypeError):
        test = ComposeDefinition(
            [f"{HERE}/valid_input.yaml", f"{HERE}/invalid_extension.yaml"]
        )


def test_fail_json_validation():
    with pytest.raises(ValidationError):
        test = ComposeDefinition([f"{HERE}/invalid_input.yaml"])


def test_invalid_ports_format():
    with pytest.raises(ValueError):
        test = ComposeDefinition([f"{HERE}/invalid_port_format.yaml"])


def test_valid_ports_strings():
    parts = PORTS_STR_RE.match("80")
    assert parts.group("target") == "80"

    parts = PORTS_STR_RE.match("81:80")
    assert parts.group("target") == "80"
    assert parts.group("published") == "81"

    parts = PORTS_STR_RE.match("80:80/tcp")
    assert parts.group("target") == "80"
    assert parts.group("published") == "80"
    assert parts.group("protocol") == "tcp"

    parts = PORTS_STR_RE.match("80:8080/udp")
    assert parts.group("target") == "8080"
    assert parts.group("published") == "80"
    assert parts.group("protocol") == "udp"


def test_invalid_ports_strings():
    assert PORTS_STR_RE.match("80abc") is None
    assert PORTS_STR_RE.match("81:80aa") is None
    assert PORTS_STR_RE.match("80:80/toienstienp") is None
