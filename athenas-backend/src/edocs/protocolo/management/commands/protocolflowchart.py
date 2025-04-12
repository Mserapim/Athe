# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from edocs.protocolo.flowchart import ProtocolFlowchart


class Command(BaseCommand):
    help = "Generates a flowchart for the movements of a protocol"

    def add_arguments(self, parser):
        parser.add_argument("code", type=str, help="any valid Protocolo code")
        parser.add_argument(
            "output",
            type=str,
            help=(
                "write graph to file (some supported formats: png, jpg, "
                "pdf, svg, dot. See Graphviz docs for more info)."
            ),
        )
        parser.add_argument(
            "--detailed",
            dest="detailed",
            action="store_true",
            help="show more details about Movimentacao",
        )
        parser.add_argument(
            "--no-colorful",
            dest="no_colorful",
            action="store_true",
            help="render graph as black and white",
        )
        parser.add_argument(
            "--no-logo",
            dest="no_logo",
            action="store_true",
            help="don't include public institution logo",
        )
        parser.add_argument(
            "--no-legend",
            dest="no_legend",
            action="store_true",
            help="don't include legend",
        )
        parser.add_argument(
            "--legend-on-top",
            dest="legend_on_top",
            action="store_true",
            help="show legend on top",
        )
        parser.add_argument(
            "--flow-to-right",
            dest="flow_to_right",
            action="store_true",
            help="change the flow layout from left to right",
        )
        parser.add_argument(
            "-x",
            "--distance-x",
            dest="distance_x",
            type=float,
            help="distance between movements along x axis",
        )
        parser.add_argument(
            "-y",
            "--distance-y",
            dest="distance_y",
            type=float,
            help="distance between movements along y axis",
        )

    def handle(self, *args, **options):
        flowchart = ProtocolFlowchart(
            protocol=options["code"],
            detailed=options.get("detailed", False),
            colorful=(not options.get("no_colorful", False)),
            no_logo=options.get("no_logo", False),
            no_legend=options.get("no_legend", False),
            legend_on_top=options.get("legend_on_top", False),
            flow_to_right=options.get("flow_to_right", False),
            distance_x=options.get("distance_x", 1.0),
            distance_y=options.get("distance_y", 1.0),
        )

        try:
            flowchart.render()
            flowchart.save_to_file(options["output"])
        except RuntimeWarning as e:
            print("RUNTIME_WARNING:", e)
        except Exception as e:
            print("ERROR:", e)
