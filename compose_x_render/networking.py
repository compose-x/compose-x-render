#   -*- coding: utf-8 -*-
#  SPDX-License-Identifier: MPL-2.0
#  Copyright 2020-2021 John Mille <john@compose-x.io>

import re


def define_protocol(port_string):
    """
    Function to define the port protocol. Defaults to TCP if not specified otherwise

    :param port_string: the port string to parse from the ports list in the compose file
    :type port_string: str
    :return: protocol, ie. udp or tcp
    :rtype: str
    """
    protocols = ["tcp", "udp"]
    protocol = "tcp"
    if port_string.find("/"):
        protocol_found = port_string.split("/")[-1].strip()
        if protocol_found in protocols:
            return protocol_found
    return protocol


def set_service_ports(ports):
    """Function to define common structure to ports

    :return: list of ports the ecs_service uses formatted according to dict
    :rtype: list
    """
    service_ports = []
    for port in ports:
        if not isinstance(port, (str, dict, int)):
            raise TypeError(
                "ports must be of types", dict, "or", list, "got", type(port)
            )
        if isinstance(port, str):
            ports_str_re = re.compile(
                r"(?:(?P<published>\d{1,5})?(?::))?(?P<target>\d{1,5})(?:(?=/(?P<protocol>udp|tcp)))?"
            )
            if not ports_str_re.match(port):
                raise ValueError(
                    f"Port {port} is not valid. Must match", ports_str_re.pattern
                )
            parts = ports_str_re.match(port)
            service_ports.append(
                {
                    "protocol": parts.group("protocol") or "tcp",
                    "published": int(parts.group("published"))
                    or int(parts.group("target")),
                    "target": int(parts.group("target")),
                    "mode": "awsvpc",
                }
            )
        elif isinstance(port, dict):
            valid_keys = ["published", "target", "protocol", "mode"]
            if not set(port).issubset(valid_keys):
                raise KeyError("Valid keys are", valid_keys, "got", port.keys())
            port["mode"] = "awsvpc"
            service_ports.append(port)
        elif isinstance(port, int):
            service_ports.append(
                {
                    "protocol": "tcp",
                    "published": port,
                    "target": port,
                    "mode": "awsvpc",
                }
            )
    return service_ports
