# -*- coding: utf-8 -*-
import textwrap
import warnings
from xml.dom import minidom

from django.template import loader
from pygraphviz import AGraph

from contrib.utils import getLogger
from edocs.protocolo.models import Protocolo as Protocol, Movimentacao as Movement
from rh.models import Servidor as Employee


log = getLogger()
supported_output_formats = ["svg", "png", "jpg", "pdf"]


class ProtocolFlowchart:
    """Generates a flowchart for the movements of a protocol.

    This class uses pygraphviz module to generate a flowchart to
    ilustrate the movements of a protocol.

    You can save the result to several formats, such as PNG, JPG,
    SVG, DOT, PDF etc.

    Arguments:

        protocol: Must be a Protocolo instance or a Protocolo code (argument required).
        detailed: True to show more details about Movimentacao (default False).
        colorful: True to render a colored graph. False will render a
          black and white graph with no legend (default True).
        no_logo: True to not include the public institution's logo (default False).
        no_legend: True to not include legend in the graph (default False).
        legend_on_top: True to show legend on top of the graph (default False).
        flow_to_right: True to flow layout from left to right (default False).
        distance_x: Distance between movements along x axis (default 1.0).
        distance_y: Distance between movements along y axis (default 1.0).

    Example use:

        >>> from edocs.protocolo.models import Protocolo as Protocol
        >>> code = '07010343837202022'
        >>> flowchart = ProtocolFlowchart(protocol=code)
        >>> try:
        >>>     flowchart.render()
        >>>     flowchart.save_to_file(f'{code}.svg')
        >>> except RuntimeWarning as e:
        >>>     print(e)
        >>> except Exception as e:
        >>>     print(e)

    Known issues:

        - You may get a "graph is too large" error when trying to
        generate a flowchart for a protocol that has thousands of
        movements. As of the date of this writing, the protocol with
        the largest number of movements is code 07010337205202021,
        accounting for 1763 movements, and its output PNG image was
        over 32k pixels wide, in addition to a very low and unusable
        quality. However, this problem is particular for PNG files,
        and you can always use the SVG format as an alternative.

    """

    class Color:
        NOT_RECEIVED = "#ffffbb"
        RECEIVED = "#bbffbb"
        FINISHED = "#ddddff"
        REOPENED = "#ffdddd"

    def __init__(
        self,
        protocol,
        detailed=False,
        colorful=True,
        no_logo=False,
        no_legend=False,
        legend_on_top=False,
        flow_to_right=False,
        distance_x=1.0,
        distance_y=1.0,
    ):
        self.protocol = protocol
        self.detailed = detailed
        self.colorful = colorful
        self.no_logo = no_logo
        self.no_legend = no_legend
        self.legend_on_top = legend_on_top
        self.flow_to_right = flow_to_right
        self.distance_x = distance_x
        self.distance_y = distance_y
        self._flowchart = None

        self.protocol = self._get_protocol()
        self.movements = self._get_movements()

    def _get_protocol(self):
        if isinstance(self.protocol, Protocol):
            return self.protocol
        elif isinstance(self.protocol, str):
            try:
                return Protocol.objects.select_related(
                    "interessado",
                    "orgao_geral_origem",
                    "servidor_origem__pessoa_fisica",
                    "tipo_documento",
                ).get(codigo=self.protocol)
            except Protocol.DoesNotExist:
                raise Exception(
                    f"Could not find any Protocolo with the provided code '{self.protocol}'."
                )
        else:
            raise Exception(
                "Parameter 'protocol' must be a Protocolo instance or Protocolo code."
            )

    def _get_movements(self):
        related_fields = (
            "destinatario__pessoafisica",
            "lotacao_origem",
            "lotacao_destino",
            "servidor_origem__user",
            "servidor_destino__user",
            "reopen_by",
            "child_of",
        )

        return self.protocol.movimentacoes.select_related(*related_fields)

    def _init_graph(self):
        self._flowchart = AGraph(strict=False, directed=True)
        self._flowchart.node_attr.update(shape="plaintext", fontname="Arial")

        self._flowchart.graph_attr.update(
            nodesep=self.distance_x,  # distance between nodes along x axis
            ranksep=self.distance_y,  # distance between nodes along y axis
        )

        if self.flow_to_right:
            self._flowchart.graph_attr.update(rankdir="LR")

    def _prepare_legend_node(self):
        rendered = loader.get_template("protocolo/flowchart/legend.html").render(
            {
                "NOT_RECEIVED": self.Color.NOT_RECEIVED,
                "RECEIVED": self.Color.RECEIVED,
                "FINISHED": self.Color.FINISHED,
                "REOPENED": self.Color.REOPENED,
                "legend_on_top": self.legend_on_top,
            }
        )

        self._flowchart.graph_attr.update(
            label=f"<{rendered}>", labelloc="t" if self.legend_on_top else "b"
        )

    def _user_from_person(self, person, only_active_employee=True):
        """Returns an User object from a Pessoa object.

        A função user_from_person nativa do Athenas não funciona bem em
        alguns casos. A implementação seguinte pretende ser uma melhoria.

        See issue mpto/athenas#483 for more details.
        """
        user = None

        if person.is_servidor():
            if only_active_employee:
                employee_set = person.pessoafisica.servidor_set.filter(ativo=True)
            else:
                employee_set = person.pessoafisica.servidor_set.order_by(
                    "-ativo"
                )  # Prioriza ativo

            for employee in employee_set:
                if employee.user:
                    user = employee.user
                    break

        return user

    def _get_destination(self, movement):
        destination = "?"

        if movement.destinatario:
            # destination = user_from_person(movement.destinatario)  # This one returns None :(
            destination = self._user_from_person(
                person=movement.destinatario, only_active_employee=False
            )
            if not destination:
                destination = movement.destinatario
        elif movement.lotacao_destino:
            if movement.lotacao_destino.sigla:
                destination = movement.lotacao_destino.sigla
            else:
                destination = movement.lotacao_destino

        return destination

    def _get_fillcolor(self, movement):
        fillcolor = "white"

        if movement.data_recebimento:
            fillcolor = self.Color.RECEIVED

        if movement.data_finalizado:
            fillcolor = self.Color.FINISHED

        if not movement.data_recebimento:
            fillcolor = self.Color.NOT_RECEIVED

        if movement.reopen_at:
            fillcolor = self.Color.REOPENED

        return fillcolor

    def _get_formatted_subject(self):
        subject = self.protocol.assunto

        if len(subject) > 72:
            subject = '<br align="left"/>'.join(textwrap.wrap(subject, width=72))
            subject = f'{subject}<br align="left"/>'

        return subject

    def _prepare_protocol_node(self):
        rendered = loader.get_template("protocolo/flowchart/protocol.html").render(
            {
                "instance": self.protocol,
                "include_logo": not self.no_logo,
                "subject": self._get_formatted_subject(),
            }
        )

        self._flowchart.add_node(
            "protocol",
            shape="note",
            style="solid",
            color="black",
            fillcolor="white",
            label=f"<{rendered}>",
        )

    def _prepare_movement_nodes(self):
        for movement in self.movements:
            destination = self._get_destination(movement)

            rendered = loader.get_template("protocolo/flowchart/movement.html").render(
                {
                    "instance": movement,
                    "destination": destination,
                    "detailed": self.detailed,
                }
            )

            self._flowchart.add_node(
                movement.id,
                shape="rect",
                style="filled,solid,rounded",
                color="black",
                fillcolor=self._get_fillcolor(movement) if self.colorful else "white",
                label=f"<{rendered}>",
            )

    def _prepare_edges(self):
        first_movement = None

        for movement in self.movements:
            if movement.child_of:
                self._flowchart.add_edge(
                    movement.child_of.id,
                    movement.id,
                    label=f"Passo {movement.passo}\n({movement.id})",
                    fontsize=9,
                )
            elif movement.passo == 0:
                first_movement = movement

        if first_movement:
            self._flowchart.add_edge(
                "protocol",
                first_movement.id,
                label=f"Passo {first_movement.passo}\n({first_movement.id})",
                fontsize=9,
            )

    def _prepare_layout(self):
        self._flowchart.layout(prog="dot")  # default neato

    def _fix_url_logo(self, path):
        """Opens SVG file to fix logo's URL.

        It's a fix because when some user downloads the SVG and opens
        it, the logo image appears broken.

        This method opens the SVG file specified by `path` and basically
        replaces the relative URL of the logo image element with an
        absolute URL.

        We do that in here because Graphviz doesn't support absolute
        URL in it's img element.

        """
        svg = minidom.parse(path)
        images = svg.getElementsByTagName("image")
        absolute_url = "https://athenas.mpto.mp.br/athenas/static/images/homedata.png"

        if len(images):
            images[0].attributes["xlink:href"].value = absolute_url

            with open(path, "w") as handler:
                svg.writexml(handler)

            svg.unlink()  # frees memory

    def save_to_file(self, path):
        """Output flowchart to path in specified format.

        An attempt will be made to guess the output format based on the
        file extension of `path`.

        Formats (not all may be available on every system depending on
        how Graphviz was built)

            'canon', 'cmap', 'cmapx', 'cmapx_np', 'dia', 'dot',
            'fig', 'gd', 'gd2', 'gif', 'hpgl', 'imap', 'imap_np',
            'ismap', 'jpe', 'jpeg', 'jpg', 'mif', 'mp', 'pcl', 'pdf',
            'pic', 'plain', 'plain-ext', 'png', 'ps', 'ps2', 'svg',
            'svgz', 'vml', 'vmlz', 'vrml', 'vtx', 'wbmp', 'xdot', 'xlib'

        Alson, this method will turn every warning raised by pygraphviz
        into an exception, so you can catch it in order to see what is
        going on.

        Example use:

            >>> flowchart.render()
            >>> try:
            >>>     flowchart.save_to_file('myflowchart.svg')
            >>> except RuntimeWarning:
            >>>     print('Something went wrong!')

        """
        if not self._flowchart:
            raise Exception(
                "You have to call the render method before "
                "trying to save the result."
            )

        with warnings.catch_warnings():
            warnings.simplefilter("error", category=RuntimeWarning)
            self._flowchart.draw(path)

        if path.endswith(".svg"):
            self._fix_url_logo(path)

    def render(self):
        """This procedure generates the flowchart.

        Creates a graph, adding nodes, edges, labels etc.

        It turns every warning raised by pygraphviz into an exception,
        so you can catch it in order to see what is going on.

        Example use:

            >>> try:
            >>>     flowchart.render()
            >>> except RuntimeWarning:
            >>>     print('Something went wrong!')

        """
        with warnings.catch_warnings():
            warnings.simplefilter(
                "error", category=RuntimeWarning
            )  # Turns warnings into exceptions

            self._init_graph()
            if self.colorful and not self.no_legend:
                self._prepare_legend_node()
            self._prepare_protocol_node()
            self._prepare_movement_nodes()
            self._prepare_edges()
            self._prepare_layout()
