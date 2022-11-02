#  SPDX-License-Identifier: MPL-2.0
#  Copyright 2020-2022 John Mille <john@compose-x.io>

"""Main module."""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Union

import jsonschema
import yaml
from importlib_resources import files as pkg_files

from compose_x_render.list_management import handle_lists_merges

try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader, Dumper

from compose_x_common.compose_x_common import keyisset

from compose_x_render.consts import PORTS, SECRETS, SERVICES, VOLUMES
from compose_x_render.envsubst import expandvars
from compose_x_render.networking import set_service_ports


def render_services_ports(services):
    """
    Function to set and render ports as docker-compose does for config

    :param dict services:
    :return:
    """
    for service_name in services:
        if keyisset(PORTS, services[service_name]):
            ports = set_service_ports(services[service_name][PORTS])
            services[service_name][PORTS] = ports


def merge_ports(source_ports, new_ports):
    """
    Function to merge two sections of ports

    :param list source_ports:
    :param list new_ports:
    :return:
    """
    f_source_ports = set_service_ports(source_ports)
    f_override_ports = set_service_ports(new_ports)
    f_overide_ports_targets = [port["target"] for port in f_override_ports]
    new_ports = []
    for port in f_override_ports:
        new_ports.append(port)
        for s_port in f_source_ports:
            if s_port["target"] not in f_overide_ports_targets:
                new_ports.append(s_port)
    return new_ports


def merge_service_definition(original_def, override_def, nested=False):
    """
    Merges two services definitions if service exists in both compose files.

    :param bool nested:
    :param dict original_def:
    :param dict override_def:
    :return:
    """

    if not nested:
        original_def = deepcopy(original_def)
    for key in override_def.keys():
        if (
            isinstance(override_def[key], dict)
            and keyisset(key, original_def)
            and isinstance(original_def[key], dict)
        ):
            merge_service_definition(original_def[key], override_def[key], nested=True)
        elif key not in original_def:
            original_def[key] = override_def[key]
        elif (
            isinstance(override_def[key], list)
            and key in original_def.keys()
            and key != "ports"
        ):
            if not isinstance(original_def[key], list):
                raise TypeError(
                    "Cannot merge",
                    key,
                    "from",
                    type(original_def[key]),
                    "with",
                    type(override_def[key]),
                )
            handle_lists_merge_conditions(
                original_def,
                override_def,
                key,
                keys_to_uniqfy=[
                    VOLUMES,
                    SECRETS,
                    "ManagedPolicyArns",
                    "AwsSources",
                    "ExtSources",
                ],
            )
        elif (
            isinstance(override_def[key], list)
            and key in original_def.keys()
            and key == "ports"
        ):
            original_def[key] = merge_ports(original_def[key], override_def[key])
        elif isinstance(override_def[key], str):
            original_def[key] = expandvars(override_def[key])
        else:
            original_def[key] = override_def[key]
    return original_def


def interpolate_env_vars(content: dict, default_empty: Union[None, str]):
    """
    Function to interpolate env vars from content for string values.
    """
    if not content:
        return
    for key in content.keys():
        if isinstance(content[key], dict):
            interpolate_env_vars(content[key], default_empty)
        elif isinstance(content[key], list):
            for count, item in enumerate(content[key]):
                if isinstance(item, dict):
                    interpolate_env_vars(item, default_empty)
                elif isinstance(item, str):
                    content[key][count] = expandvars(item, default=default_empty)
        elif isinstance(content[key], str):
            content[key] = expandvars(
                content[key], default=default_empty, skip_escaped=True
            )


def merge_services_from_files(original_services: dict, override_services: dict) -> None:
    """
    Function to merge two docker compose files content.

    """
    for service_name in override_services:
        if keyisset(service_name, original_services):
            original_services.update(
                {
                    service_name: merge_service_definition(
                        original_services[service_name],
                        override_services[service_name],
                    )
                }
            )
        else:
            original_services.update({service_name: override_services[service_name]})


def handle_lists_merge_conditions(
    original_def: dict, override_def: dict, key: str, keys_to_uniqfy: list[str]
) -> None:
    """
    Function to handle lists merging and whether some additional handling is necessary for duplicates

    :param dict original_def: The src definition
    :param dict override_def: The override definition to merge to src.
    :param str key: The key name of the list object
    :param list[dict] keys_to_uniqfy: List of keys in the dict definition that require unique items.
    """
    if not isinstance(original_def[key], list):
        raise TypeError(
            "Cannot merge",
            key,
            "from",
            type(original_def[key]),
            "with",
            type(override_def[key]),
        )
    if key in keys_to_uniqfy:
        original_def[key] = handle_lists_merges(
            original_def[key], override_def[key], uniqfy=True
        )
    else:
        original_def[key] = handle_lists_merges(
            original_def[key], override_def[key], uniqfy=False
        )


def load_compose_file(file_path) -> Union[dict, list]:
    """
    Read docker compose file content and load with YAML
    """
    with open(file_path) as composex_fd:
        return yaml.load(composex_fd.read(), Loader=Loader)


def merge_definitions(
    original_def: dict, override_def: dict, nested: bool = False
) -> dict:
    """
    Merges resources and non services definitions together.
    """
    if not nested:
        original_def = deepcopy(original_def)
    elif not isinstance(override_def, dict):
        raise TypeError("Expected", dict, "got", type(override_def))
    for key in override_def.keys():
        if (
            isinstance(override_def[key], dict)
            and keyisset(key, original_def)
            and isinstance(original_def[key], dict)
        ):
            merge_definitions(original_def[key], override_def[key], nested=True)
        elif key not in original_def:
            original_def[key] = override_def[key]
        elif isinstance(override_def[key], list) and key in original_def.keys():
            handle_lists_merge_conditions(
                original_def,
                override_def,
                key,
                keys_to_uniqfy=[
                    "ManagedPolicyArns",
                    "AwsSources",
                    "ExtSources",
                ],
            )
        elif isinstance(override_def[key], list) and key not in original_def.keys():
            original_def[key]: list = []
            handle_lists_merge_conditions(
                original_def,
                override_def,
                key,
                keys_to_uniqfy=[
                    "ManagedPolicyArns",
                    "AwsSources",
                    "ExtSources",
                ],
            )

        elif isinstance(override_def[key], str):
            original_def[key] = expandvars(override_def[key])
        else:
            original_def[key] = override_def[key]
    for key, value in original_def.items():
        if isinstance(value, list) and key in [VOLUMES, SECRETS]:
            original_def[key] = handle_lists_merges(value, [], uniqfy=True)
    return original_def


def merge_config_files(original_content: dict, override_content: dict) -> None:
    """
    Function to merge everything that is not services.
    For services, we use function merge_services_from_files
    For x-resources and everything else, use merge_definitions
    """

    for compose_key in override_content:
        if (
            compose_key == SERVICES
            and keyisset(compose_key, original_content)
            and keyisset(compose_key, override_content)
        ):
            original_services = original_content[SERVICES]
            override_services = override_content[SERVICES]
            merge_services_from_files(original_services, override_services)

        elif (
            keyisset(compose_key, original_content)
            and isinstance(original_content[compose_key], dict)
            and not compose_key == SERVICES
        ):
            original_definition = deepcopy(original_content[compose_key])
            override_definition = override_content[compose_key]
            original_content.update(
                {
                    compose_key: merge_definitions(
                        original_definition,
                        override_definition,
                    )
                }
            )
        elif not keyisset(compose_key, original_content):
            original_content[compose_key] = override_content[compose_key]


class ComposeDefinition:
    input_file_arg = "ComposeFiles"
    compose_x_arg = "ForCompose-X"

    def __init__(
        self,
        files_list: list[str],
        content: dict = None,
        no_interpolate: bool = False,
        keep_if_undefined: bool = False,
    ):
        """
        Main function to define and merge the content of the docker files

        :param list files_list: list of files (path) to merge
        :param dict content:
        """
        if content is None and len(files_list) == 1:
            self.definition = load_compose_file(files_list[0])
        elif content is None and len(files_list) > 1:
            self.definition = load_compose_file(files_list[0])
            files_list.pop(0)
            for file in files_list:
                merge_config_files(self.definition, load_compose_file(file))

        elif content and isinstance(content, dict):
            self.definition = content
        if keyisset(SERVICES, self.definition):
            render_services_ports(self.definition[SERVICES])
        default_empty = None if keep_if_undefined else ""
        if not no_interpolate:
            interpolate_env_vars(self.definition, default_empty)
        source = pkg_files("compose_x_render").joinpath("compose-spec.json")
        jsonschema.validate(
            self.definition,
            json.loads(source.read_text()),
        )

    def write_output(
        self, output_file: str = None, for_compose_x: bool = False
    ) -> None:
        """
        Method to write the content down into a file

        :param output_file:
        :param for_compose_x:
        :return:
        """
        if for_compose_x:
            output = {
                "Fn::Transform": {
                    "Name": "compose-x",
                    "Parameters": {"Raw": self.definition},
                }
            }
        else:
            output = self.definition
        if not output_file:
            print(yaml.safe_dump(output))
        else:
            with open(output_file, "w") as file_fd:
                file_fd.write(yaml.safe_dump(output))

    def output_services_images(self, output_file: str = None):
        output_map = {}
        for name, service in self.definition[SERVICES].items():
            if keyisset("image", service):
                output_map[name] = service["image"]
            else:
                print(f"Service {name} has no image defined. Skipping")
        if output_file:
            with open(output_file, "w") as file_fd:
                file_fd.write(json.dumps(output_map))
        else:
            print(json.dumps(output_map, indent=2))
