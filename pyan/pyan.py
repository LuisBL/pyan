#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    pyan.py - Generate approximate call graphs for Python programs.

    This program takes one or more Python source files, does a superficial
    analysis, and constructs a directed graph of the objects in the combined
    source, and how they define or use each other.  The graph can be output
    for rendering by e.g. Graphviz or yEd.
"""

import argparse
import logging
from glob import glob
import os.path
import sys

from pyan.analyzer import CallGraphVisitor
from pyan.visgraph import VisualGraph
from pyan.writers import TgfWriter, DotWriter, YedWriter, DotRenderer, NoDotError


def process_command_line(argv):
    # script_name = argv[0]
    argv = argv[1:]

    desc = (
        "Analyse one or more Python source files and generate an"
        "approximate call graph of the modules, classes and functions"
        " within them."
    )

    # initialize the parser object:
    parser = argparse.ArgumentParser(description=desc)

    # required arguments
    parser.add_argument("filename", nargs="+", help="Python files to process")

    # optional arguments

    # output formats
    parser.add_argument(
        "--format",
        help=(
            "Output in FORMAT file format.  Especially useful when outputting"
            " to stdout when no --file output file is specified."
            " FORMAT may be one of:"
            " png, svg, webp, pdf, eps, ps, dot (Graphviz),"
            " tgf (Tivial Graph Format), yed (yEd GraphML)"
        ),
    )

    parser.add_argument(
        "-f",
        "--file",
        dest="outfilename",
        help=(
            "write graph to FILE.  If no file format is specified using the"
            " --format option, then the extension of FILE will be used to"
            " determine desired output file format."
        ),
        metavar="FILE",
        default=None,
    )

    # drawing options
    parser.add_argument(
        "-d",
        "--defines",
        action="store_true",
        default=False,
        dest="draw_defines",
        help="add edges for 'defines' relationships",
    )
    parser.add_argument(
        "-N",
        "--no-uses",
        action="store_false",
        default=True,
        dest="draw_uses",
        help="do not add edges for 'uses' relationships",
    )
    grouped_group = parser.add_mutually_exclusive_group()
    grouped_group.add_argument(
        "-G",
        "--grouped-alt",
        action="store_true",
        default=False,
        dest="grouped_alt",
        help="suggest grouping by adding invisible defines edges [only useful without --defines]",
    )
    grouped_group.add_argument(
        "-g",
        "--grouped",
        action="store_true",
        default=False,
        dest="grouped",
        help="group nodes (create subgraphs) according to namespace [dot only]",
    )

    parser.add_argument(
        "-k",
        "--uncolored",
        action="store_false",
        default=True,
        dest="colored",
        help="do not color nodes according to namespace [dot only]",
    )
    parser.add_argument(
        "-e",
        "--nested-groups",
        action="store_true",
        default=False,
        dest="nested_groups",
        help="create nested groups (subgraphs) for nested namespaces (implies -g) [dot only]",
    )
    parser.add_argument(
        "-a",
        "--annotated",
        action="store_true",
        default=False,
        dest="annotated",
        help="annotate with module and source line number",
    )
    parser.add_argument(
        "--dot-rankdir",
        default="TB",
        dest="rankdir",
        help=(
            "specifies the dot graph 'rankdir' property for "
            "controlling the direction of the graph. "
            "Allowed values: ['TB', 'LR', 'BT', 'RL']. "
            "[dot only]"
        ),
    )

    # general options
    parser.add_argument(
        "-l", "--log", dest="logname", help="write log to LOG", metavar="LOG"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        dest="verbose",
        help="verbose output. (Use twice for very verbose)",
    )

    args = parser.parse_args(argv)

    return args


def main():
    args = process_command_line(sys.argv)

    filenames = [y for x in args.filename for y in glob(x)]

    if args.nested_groups:
        args.grouped = True

    graph_options = {
        "draw_defines": args.draw_defines,
        "draw_uses": args.draw_uses,
        "colored": args.colored,
        "grouped_alt": args.grouped_alt,
        "grouped": args.grouped,
        "nested_groups": args.nested_groups,
        "annotated": args.annotated,
    }

    out_format = args.format
    if args.outfilename and not args.format:
        out_format = os.path.splitext(args.outfilename)[1][1:]
    if not out_format:
        out_format = "dot"

    logger = logging.getLogger(__name__)
    if args.verbose >= 2:
        logger.setLevel(logging.DEBUG)
    elif args.verbose == 1:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARN)
    logger.addHandler(logging.StreamHandler())
    if args.logname:
        handler = logging.FileHandler(args.logname)
        logger.addHandler(handler)

    v = CallGraphVisitor(filenames, logger)
    graph = VisualGraph.from_visitor(v, options=graph_options, logger=logger)

    if out_format == "dot":
        writer = DotWriter(
            graph,
            options=["rankdir=" + args.rankdir],
            output=args.outfilename,
            logger=logger,
        )
    elif out_format == "tgf":
        writer = TgfWriter(graph, output=args.outfilename, logger=logger)
    elif out_format == "yed":
        writer = YedWriter(graph, output=args.outfilename, logger=logger)
    elif out_format in ["svg", "png", "eps", "pdf", "ps", "webp"]:
        try:
            writer = DotRenderer(
                graph,
                options=["rankdir=" + args.rankdir],
                output=args.outfilename,
                output_format=out_format,
                logger=logger,
            )
        except NoDotError:
            print(
                "No executable 'dot' found in PATH.  Stopping without creating"
                " any output."
            )
            print(
                "To enable this functionality, install Graphviz's dot utility"
                " to your path."
            )
            return
    else:
        print("Cannot determine output format.  Stopping without creating any output.")
        return
    # actually write file output
    writer.run()


if __name__ == "__main__":
    main()
