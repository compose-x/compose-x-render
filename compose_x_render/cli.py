#  -*- coding: utf-8 -*-
# SPDX-License-Identifier: MPL-2.0
# Copyright 2020-2021 John Mille <john@compose-x.io>

"""Console script for compose_x_render."""

import argparse
import sys

from compose_x_render.compose_x_render import ComposeDefinition


def main():
    """Console script for compose_x_render."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--docker-compose-file",
        dest=ComposeDefinition.input_file_arg,
        required=True,
        help="Path to the Docker compose file",
        action="append",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        required=False,
        help="Output directory to write all the templates to.",
        default=None,
    )
    parser.add_argument(
        "-x",
        "--compose-x-macro",
        required=False,
        help="Auto-Format for ECS Compose-X CFN Macro",
        action="store_true",
        dest=ComposeDefinition.compose_x_arg,
        default=False,
    )
    parser.add_argument(
        "--no-interpolate",
        help="Preserves environment variables and leaves text as-is.",
        action="store_true",
        default=False,
    )
    parser.add_argument("_", nargs="*")
    args = parser.parse_args()
    kwargs = vars(args)
    compose_file = ComposeDefinition(kwargs[ComposeDefinition.input_file_arg], no_interpolate=args.no_interpolate)
    compose_file.write_output(args.output_file, kwargs[ComposeDefinition.compose_x_arg])
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
