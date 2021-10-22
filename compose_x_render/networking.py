#   -*- coding: utf-8 -*-
#  SPDX-License-Identifier: MPL-2.0
#  Copyright 2020-2021 John Mille <john@compose-x.io>

import re


def set_service_ports(ports):
    """Function to define common structure to ports

    :return: list of ports the ecs_service uses formatted according to dict
    :rtype: list
    """
    service_ports = []
    for port in ports:
        if isinstance(port, str):
            ports_str_re = re.compile(
                r"(?:(?P<published>\d{1,5})?(?::))?(?P<target>\d{1,5})(?:(?=/(?P<protocol>udp|tcp)))?"
            )
            parts = ports_str_re.match(port)
            if not parts:
                raise ValueError(
                    f"Port {port} is not valid. Must match", ports_str_re.pattern
                )
            port = {
                "protocol": parts.group("protocol") or "tcp",
                "published": int(parts.group("published"))
                if isinstance(parts.group("published"), str)
                else int(parts.group("target")),
                "target": int(parts.group("target")),
                "mode": "awsvpc",
            }
        elif isinstance(port, dict):
            port["mode"] = "awsvpc"
        elif isinstance(port, int):
            port = {
                "protocol": "tcp",
                "published": port,
                "target": port,
                "mode": "awsvpc",
            }
        if port["published"] not in [s_port["published"] for s_port in service_ports]:
            service_ports.append(port)
        else:
            print(f"Port {port['published']} is already defined", port, "Skipping")
    return service_ports
