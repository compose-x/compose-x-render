#  -*- coding: utf-8 -*-
# SPDX-License-Identifier: MPL-2.0
# Copyright 2020-2021 John Mille <john@compose-x.io>

"""Main module."""

from copy import deepcopy

import yaml

try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader, Dumper

from compose_x_render.consts import PORTS, SECRETS, SERVICES, VOLUMES
from compose_x_render.envsubst import expandvars
from compose_x_render.networking import set_service_ports


def keyisset(x, y):
    """
    Macro to figure if the the dictionary contains a key and that the key is not empty

    :param str x: The key to check presence in the dictionary
    :param dict y: The dictionary to check for

    :returns: True/False
    :rtype: bool
    """
    if isinstance(y, dict) and x in y.keys() and y[x]:
        return True
    return False


def keypresent(x, y):
    """
    Macro to figure if the the dictionary contains a key and that the key is not empty

    :param str x: The key to check presence in the dictionary
    :param dict y: The dictionary to check for

    :returns: True/False
    :rtype: bool
    """
    if isinstance(y, dict) and x in y.keys():
        return True
    return False


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
        if isinstance(override_def[key], dict) and keyisset(key, original_def) and isinstance(original_def[key], dict):
            merge_service_definition(original_def[key], override_def[key], nested=True)
        elif key not in original_def:
            original_def[key] = override_def[key]
        elif isinstance(override_def[key], list) and key in original_def.keys() and key != "ports":
            if not isinstance(original_def[key], list):
                raise TypeError(
                    "Cannot merge",
                    key,
                    "from",
                    type(original_def[key]),
                    "with",
                    type(override_def[key]),
                )
            original_def[key] = handle_lists_merges(original_def[key], override_def[key])
        elif isinstance(override_def[key], list) and key in original_def.keys() and key == "ports":
            original_def[key] = merge_ports(original_def[key], override_def[key])
        elif isinstance(override_def[key], str):
            original_def[key] = expandvars(override_def[key])
        else:
            original_def[key] = override_def[key]
    return original_def


def interpolate_env_vars(content, default_empty):
    """
    Function to interpolate env vars from content

    :param dict content:
    :return:
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
            content[key] = expandvars(content[key], default=default_empty, skip_escaped=True)


def merge_services_from_files(original_services, override_services):
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


def handle_lists_merges(original_list, override_list, uniqfy=False):
    """

    :param list original_list: The original list to add the override ones to
    :param list override_list: The lost of items to add up
    :param bool uniqfy: Whether you are expecting identical dicts which should be filtered to be uniqu based on values.
    :return: The merged list
    :rtype: list
    """
    final_list = []

    final_list += [item for item in original_list if isinstance(item, dict)]
    final_list += [item for item in override_list if isinstance(item, dict)]
    if uniqfy:
        final_list = [dict(y) for y in set(tuple(x.items()) for x in final_list)]
    original_str_items = [item for item in original_list if isinstance(item, list)]
    final_list += list(set(original_str_items + [item for item in override_list if isinstance(item, list)]))

    origin_list_items = [item for item in original_list if isinstance(item, list)]
    override_list_items = [item for item in override_list if isinstance(item, list)]

    if origin_list_items and override_list_items:
        merged_lists = handle_lists_merges(origin_list_items, override_list_items)
        final_list += merged_lists
    elif origin_list_items and not override_list_items:
        final_list += origin_list_items
    elif not origin_list_items and override_list_items:
        final_list += override_list_items
    return final_list


def handle_lists_merge_conditions(original_def, override_def, key):
    """
    Function to handle lists merging and whether some additional handling is necessary for duplicates

    :param dict original_def: The src definition
    :param dict override_def: The override definition to merge to src.
    :param str key: The key name of the list object
    """
    keys_to_uniqfy = [VOLUMES, SECRETS]
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
        original_def[key] = handle_lists_merges(original_def[key], override_def[key], uniqfy=True)
    else:
        original_def[key] = handle_lists_merges(original_def[key], override_def[key], uniqfy=False)


def load_compose_file(file_path):
    """
    Read docker compose file content and load via YAML

    :param str file_path: path to the docker compose file
    :return: content of the docker file
    :rtype: dict
    """
    with open(file_path, "r") as composex_fd:
        return yaml.load(composex_fd.read(), Loader=Loader)


def merge_definitions(original_def, override_def, nested=False):
    """
    Merges two services definitions if service exists in both compose files.

    :param bool nested:
    :param dict original_def:
    :param dict override_def:
    :return:
    """
    if not nested:
        original_def = deepcopy(original_def)
    elif not isinstance(override_def, dict):
        raise TypeError("Expected", dict, "got", type(override_def))
    for key in override_def.keys():
        if isinstance(override_def[key], dict) and keyisset(key, original_def) and isinstance(original_def[key], dict):
            merge_definitions(original_def[key], override_def[key], nested=True)
        elif key not in original_def:
            original_def[key] = override_def[key]
        elif isinstance(override_def[key], list) and key in original_def.keys():
            handle_lists_merge_conditions(original_def, override_def, key)
        elif isinstance(override_def[key], list) and key not in original_def.keys():
            original_def[key] = override_def[key]

        elif isinstance(override_def[key], str):
            original_def[key] = expandvars(override_def[key])
        else:
            original_def[key] = override_def[key]
    return original_def


def merge_config_files(original_content, override_content):
    """
    Function to merge everything that is not services

    :param dict original_content:
    :param dict override_content:
    :return:
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


class ComposeDefinition(object):

    input_file_arg = "ComposeFiles"
    compose_x_arg = "ForCompose-X"

    def __init__(self, files_list, content=None, no_interpolate=False, keep_if_undefined=False):
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

    def write_output(self, output_file=None, for_compose_x=False):
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
            print(yaml.dump(output, Dumper=Dumper))
        else:
            with open(output_file, "w") as file_fd:
                file_fd.write(yaml.dump(output, Dumper=Dumper))
