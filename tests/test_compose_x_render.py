#!/usr/bin/env python

"""Tests for `compose_x_render` package."""

import os
from os import path
from tempfile import TemporaryDirectory
from unittest import mock

import pytest
from jsonschema.exceptions import ValidationError

from compose_x_render.compose_x_render import ComposeDefinition
from compose_x_render.envsubst import expandvars
from compose_x_render.networking import PORTS_STR_RE, set_service_ports

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


def test_service_ports_names():
    ports_input: list = [
        "8080:80/tcp",
        {"target": 443, "published": 443, "protocol": "tcp"},
        {"target": 8443, "published": 8443, "protocol": "tcp", "name": "alt_https"},
        {"target": 69, "published": 69, "protocol": "udp"},
    ]
    service_ports = set_service_ports(ports_input)
    port_names = [_port["name"] for _port in service_ports]
    assert "tcp_80" in port_names
    assert "tcp_443" in port_names
    assert "udp_69" in port_names
    assert "alt_https" in port_names
