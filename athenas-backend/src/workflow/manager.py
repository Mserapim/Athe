# -*- coding:utf-8 -*-

from django.db import models, transaction
from contrib.utils import getLogger
from workflow import misc

log = getLogger(__name__)


# Fallback do modulo transaction entre o django 1.8 e versões anteriores
if not hasattr(transaction, "atomic"):
    transaction.atomic = transaction.commit_on_success


class CommonManager(models.Manager):

    def get_latest(self, *args, **kwargs):
        if len(args) == 1:
            kwargs = dict(id=args[0])
        qs = self.list(**kwargs)
        return qs.latest("id") if qs.exists() else None

    def list(self, **kwargs):
        if type(kwargs) is not dict:
            kwargs = dict()
        kwargs["active"] = True
        return self.model.objects.filter(**kwargs)

    def create_or_edit(self, request):
        """Create or edit a workflow"""
        params = getattr(request, "data", {})

        try:
            common = self.get(params["id"]) if params.get("id") else self.model()
            common.name = params["name"]
            common.description = params["description"]

            with transaction.atomic():
                common.save()

        except Exception as e:
            log.exception(e)
            raise e

        return common


class JokerManager(CommonManager):
    pass


class WorkflowManager(CommonManager):
    pass


class VertexManager(CommonManager):

    def create_or_edit(self, request):
        """Create or edit a vertex"""
        params = getattr(request, "data", {})

        try:
            model = misc.evaluate(params["kind"])
            vertex = model.objects.get(id=params["id"]) if params.get("id") else model()
            vertex.name = params["name"]
            vertex.description = params["description"]
            vertex.acronym = params["acronym"]
            vertex.kind = params["kind"]
            vertex.beginning = bool(params["beginning"])
            vertex.workflow_id = params["workflow"]
            vertex.objective_id = params["objective"]

            with transaction.atomic():
                vertex.save()

        except Exception as e:
            log.exception(e)
            raise e

        return vertex

    def objective_list(self):
        return [
            dict(id=item.pk, name=str(item)) for item in self.model.model.objects.all()
        ]


class EdgeManager(models.Manager):

    def create_or_edit(self, request):
        """Create or edit a edge"""

        try:
            from workflow.models import Vertex

            params = getattr(request, "data", {})
            edge = (
                self.model.objects.get(edge_hash=params["edge_hash"])
                if params.get("edge_hash")
                else self.model()
            )
            edge.slug = params["slug"]
            edge.source = Vertex.objects.get(id=params["source"])
            edge.target = Vertex.objects.get(id=params["target"])

            with transaction.atomic():
                edge.save()

        except Exception as e:
            log.exception(e)
            raise e

        return edge
