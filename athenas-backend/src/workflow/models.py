# -*- coding:utf-8 -*-

import os
import hashlib

from django.db import models, transaction
from django.template.defaultfilters import slugify
from contrib.utils import getLogger
from contrib.decorator import to_search
from rh import models as rh
from workflow import manager as custom_manager
from workflow import misc
from pygraphviz import AGraph


log = getLogger(__name__)


class Common(models.Model):
    objects = custom_manager.CommonManager()

    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500, null=True, blank=True)
    active = models.BooleanField(default=True, db_index=True)

    @transaction.atomic
    def deactive(self, request=None):
        self.active = False
        self.save()

    def __str__(self):
        return str(self.name)


class Joker(Common):
    objects = custom_manager.JokerManager()


@to_search(
    [
        {"name": "name", "type": "text"},
        {"name": "description", "type": "text"},
    ]
)
class Workflow(Common):
    """Defines graph scope"""

    objects = custom_manager.WorkflowManager()
    common_ptr = models.OneToOneField(
        Common,
        parent_link=True,
        related_name="workflow_child",
        on_delete=models.CASCADE,
    )  # Parametro "on_delete" adicionado. (Django 2)

    def _read_nodes(self, graph):
        count = 1

        graph.add_node("Inicio", **{"shape": "point", "label": "Inicio"})

        for vertice in self.vertices.order_by("-beginning"):
            graph.add_node(
                vertice.acronym,
                **{
                    "label": vertice.name,
                    "color": vertice.color,
                    "shape": vertice.shape,
                    "penwidth": 1.0,
                }
            )

            count += 1

    def _read_vertices_edges(self, graph):
        for vertice in self.vertices.order_by("-beginning"):
            self._read_vertice_edge(graph, vertice)

    def _read_vertice_edge(self, graph, edge_from):
        node = graph.get_node(edge_from.acronym)
        beginnings = []
        for edge_to in edge_from.vertices.all():
            for edge in Edge.objects.filter(source=edge_from, target=edge_to):
                graph.add_edge(node, edge_to.acronym, **{"label": edge.slug})

                if edge_to.beginning is True:
                    beginnings.append(edge_to)

                zero = graph.get_node("Inicio")
                for b in beginnings:
                    graph.add_edge(zero, b.acronym)

    def draw_graph(self):
        filename = "/tmp/%s.svg" % slugify(self.name)
        log.info("graph filename: %s" % filename)

        graph = AGraph(
            **{"directed": True, "stricted": True, "rankdir": "TD", "splines": True}
        )

        self._read_nodes(graph)
        self._read_vertices_edges(graph)
        graph.graph_attr["epsilon"] = "0.001"

        graph.draw(filename, prog="dot")

        return filename


class Vertex(Common):
    """Vertex of graph"""

    __sub_classes = []
    objects = custom_manager.VertexManager()

    acronym = models.CharField(max_length=40)
    kind = models.CharField(max_length=200)
    beginning = models.BooleanField(default=False, db_index=True)
    workflow = models.ForeignKey(
        Workflow, related_name="vertices", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    vertices = models.ManyToManyField(
        "self", through="Edge", symmetrical=False, related_name="backward_vertices"
    )

    @property
    def color(self):
        if self.vertices.exists() is True:
            return "#000000" if self.beginning is False else "#0000ff"
        else:
            return "#ff0000"

    @property
    def shape(self):
        return "box" if self.vertices.exists() is True else "box"

    def next(self, slug):
        qs = Edge.objects.filter(slug=slug, source=self)
        if qs.exists():
            vertex = qs[0].target
            return vertex

    def get_objective(self):
        return misc.evaluate(self.kind).objects.get(id=self.id).objective

    @classmethod
    def register_subclass(self, sub_class):
        canonical_name = self.get_canonical_name(sub_class)
        if canonical_name not in self.__sub_classes:
            self.__sub_classes.append(canonical_name)

    @classmethod
    def get_canonical_name(self, cls):
        return "%s.%s" % (cls.__module__, cls.__name__)

    @classmethod
    def get_subclasses(self):
        return self.__sub_classes


class Edge(models.Model):
    objects = custom_manager.EdgeManager()

    slug = models.SlugField(max_length=200, db_index=True)
    source = models.ForeignKey(
        Vertex, related_name="source_edge", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    target = models.ForeignKey(
        Vertex, related_name="target_edge", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)
    edge_hash = models.CharField(max_length=32, db_index=True, blank=True, null=True)

    class Meta:
        unique_together = ("slug", "source", "target")

    def save(self, *args, **kwargs):
        self.edge_hash = hashlib.md5(os.urandom(128)).hexdigest()
        super(Edge, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.slug)


class LotacaoVertex(Vertex):
    model = rh.Lotacao
    objects = custom_manager.VertexManager()
    objective = models.ForeignKey(
        model, related_name="vertices", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)


Vertex.register_subclass(LotacaoVertex)


class ServidorVertex(Vertex):
    model = rh.Servidor
    objects = custom_manager.VertexManager()
    objective = models.ForeignKey(
        model, related_name="vertices", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)


Vertex.register_subclass(ServidorVertex)


class PessoaVertex(Vertex):
    model = rh.Pessoa
    objects = custom_manager.VertexManager()
    objective = models.ForeignKey(
        model, related_name="vertices", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)


Vertex.register_subclass(PessoaVertex)


class JokerVertex(Vertex):
    model = Joker
    objects = custom_manager.VertexManager()
    objective = models.ForeignKey(
        model, related_name="vertices", on_delete=models.CASCADE
    )  # Parametro "on_delete" adicionado. (Django 2)


Vertex.register_subclass(JokerVertex)
