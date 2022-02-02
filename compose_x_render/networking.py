#   -*- coding: utf-8 -*-
#  SPDX-License-Identifier: MPL-2.0
#  Copyright 2020-2021 John Mille <john@compose-x.io>

import re

PORTS_STR_RE = re.compile(
    r"(?:(?P<published>[\d]{1,5}):)?(?:(?P<target>\d{1,5})(?:$|(?=/(?P<protocol>tcp$|udp$))))"
)


def set_service_ports(ports):
    """Function to define common structure to ports

    :return: list of ports the ecs_service uses formatted according to dict
    :rtype: list
    """
    service_ports = []
    for src_port in ports:
        the_port = {}
        if isinstance(src_port, str):

            parts = PORTS_STR_RE.match(src_port)
            if not parts:
                raise ValueError(
                    f"Port {src_port} is not valid. Must match", PORTS_STR_RE.pattern
                )
            the_port = {
                "protocol": parts.group("protocol") or "tcp",
                "published": int(parts.group("published"))
                if isinstance(parts.group("published"), str)
                else int(parts.group("target")),
                "target": int(parts.group("target")),
                "mode": "awsvpc",
            }
        elif isinstance(src_port, dict):
            the_port = src_port
            the_port["mode"] = "awsvpc"
        elif isinstance(src_port, int):
            the_port = {
                "protocol": "tcp",
                "published": src_port,
                "target": src_port,
                "mode": "awsvpc",
            }
        if not service_ports:
            service_ports.append(the_port)
        elif service_ports and the_port["published"] not in [
            s_port["published"] for s_port in service_ports if "published" in s_port
        ]:
            service_ports.append(the_port)
        else:
            print(
                f"Port {the_port['published']} is already defined", src_port, "Skipping"
            )
    return service_ports
