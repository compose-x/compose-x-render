#  SPDX-License-Identifier: MPL-2.0
#  Copyright 2020-2021 John Mille <john@compose-x.io>

import re

from compose_x_common.compose_x_common import keyisset, set_else_none

PORTS_STR_RE = re.compile(
    r"(?:(?P<published>[\d]{1,5}):)?(?:(?P<target>\d{1,5})(?:$|(?=/(?P<protocol>tcp$|udp$))))"
)


def handle_str_definition(src_port: str) -> dict:
    parts = PORTS_STR_RE.match(src_port)
    if not parts:
        raise ValueError(
            f"Port {src_port} is not valid. Must match", PORTS_STR_RE.pattern
        )
    the_port = {
        "protocol": parts.group("protocol") or "tcp",
        "target": int(parts.group("target")),
    }
    if isinstance(parts.group("published"), str):
        the_port["published"] = int(parts.group("published"))
    return the_port


def replace_published_port(
    service_ports: list, published_port: int, new_definition: dict
) -> None:
    """
    Docker compose behaviour when two published ports have the same value, the final value for the target
    is the one of the last port defined in the list.

    This function swaps the

    :param list service_ports:
    :param int published_port:
    :param dict new_definition:
    """
    for port in service_ports:
        if keyisset("published", port) and port["published"] == published_port:
            port["target"] = new_definition["target"]
            break


def add_port_to_service_ports(service_ports: list, new_port: dict) -> None:
    """
    Adds the new port to the service ports definition.
    If the port has ``published`` defined, checks whether it can be added or needs updating the target
    if already defined.

    :param service_ports:
    :param new_port:
    :return:
    """
    same_protocol_published_ports = [
        s_port
        for s_port in service_ports
        if s_port["protocol"] == new_port["protocol"] and keyisset("published", s_port)
    ]
    same_protocol_target_not_published_ports = [
        s_port
        for s_port in service_ports
        if s_port["protocol"] == new_port["protocol"]
        and not keyisset("published", s_port)
    ]
    if not service_ports:
        service_ports.append(new_port)
    elif service_ports and not keyisset("published", new_port):
        if new_port["target"] not in [
            _port["target"] for _port in same_protocol_target_not_published_ports
        ]:
            service_ports.append(new_port)
    elif service_ports and keyisset("published", new_port):

        if new_port["published"] not in [
            _port["published"] for _port in same_protocol_published_ports
        ]:
            service_ports.append(new_port)
        elif new_port["published"] in [
            _port["published"] for _port in same_protocol_published_ports
        ]:
            replace_published_port(service_ports, new_port["published"], new_port)


def set_service_ports(ports):
    """Function to define common structure to ports

    :return: list of ports the ecs_service uses formatted according to dict
    :rtype: list
    """
    service_ports = []
    for src_port in ports:
        the_port = {}
        if isinstance(src_port, str):
            the_port = handle_str_definition(src_port)
        elif isinstance(src_port, dict):
            the_port = src_port
            the_port["protocol"] = set_else_none("protocol", src_port, "tcp")
        elif isinstance(src_port, int):
            the_port = {
                "protocol": "tcp",
                "target": src_port,
            }
        add_port_to_service_ports(service_ports, the_port)
    return service_ports
