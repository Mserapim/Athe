# -*- coding:utf-8 -*-

from functools import partial

from contrib.controller import ContentType
from contrib.decorator import login_required, validate

# APP imports
from contrib.extjs import ExtWidget
from workflow import forms, misc, models


class __Common(ExtWidget):

    model = models.Common

    @login_required(type="JSON")
    @ContentType("text/javascript")
    def json(self, args=[]):
        self.render("new toolkit.workflow.Workflow()")

    @login_required(type="JSON")
    @ContentType("text/javascript")
    def list(self, args=[]):
        kwargs = misc.extract_params(self.request)
        start, end = misc.get_slice(self.request)
        qs = self.model.objects.list(**kwargs)
        self.render({"total": qs.count(), "result": list(qs.values())})

    @login_required(type="JSON")
    @ContentType("text/javascript")
    def create_or_edit(self, args=[]):
        response = dict(success=False, msg="Não foi possível realizar operação!")
        try:
            self.model.objects.create_or_edit(self.request)
        except Exception as e:
            self.log.exception(e)
            self.log.error(e)
            response["msg"] += "<br/>%s" % str(e).replace("\n", "")
        else:
            response = dict(success=True, msg="Realizado com sucesso.")
        self.render(response)

    @login_required(type="JSON")
    @validate(forms.DeactivateForm)
    @ContentType("text/javascript")
    def delete(self, args=[]):
        response = dict(success=False, msg="Não foi possível realizar a operação!")
        model = self.model.objects.get(pk=self.request.data["id"])
        try:
            model.deactive()
        except Exception as e:
            self.log.error(e)
            response["msg"] += "<br/>%s" % e
        else:
            response = dict(success=True, msg="Realizado com sucesso.")
        self.render(response)


class WWorkflow(__Common):

    model = models.Workflow

    @login_required(type="JSON")
    @ContentType("text/javascript")
    def json(self, args=[]):
        self.render("new toolkit.workflow.Workflow()")

    @login_required(type="JSON")
    @ContentType("text/javascript")
    def show_graph(self, args=[]):
        workflow = self.request.REQUEST.get("workflow")
        vertices = models.Vertex.objects.list(workflow=workflow)
        output = ["<ul>"]
        for vertex in vertices:
            output.append("<li>De <span>%s</span> pode chegar em:</li>" % vertex)
            output.append("<ul>")
            for edge in models.Edge.objects.filter(source=vertex):
                output.append(
                    "<li><span>%s</span> através da aresta: <i>%s</i></li>"
                    % (edge.target, edge.slug)
                )
            output.append("</ul>")
        output.append("</ul>")
        output = "".join(output)
        self.render('<div class="workflow-graph">%s</div>' % output)

    @validate(forms.WorkflowForm)
    def create_or_edit(self, args=[]):
        super(Workflow, self).create_or_edit(*args)

    def graph(self, args=[]):
        try:
            w = models.Workflow.objects.get(pk=args[0])
            # self.response['content-type'] = 'image/svg+xml'
            with open(w.draw_graph()) as fd:
                for chunk in iter(partial(fd.read, 8192), b""):
                    self.response.write(chunk)
        except Exception as e:
            self.log.exception(e)
            self.response.write(
                [w.pk for w in models.Workflow.objects.all()] + [str(e)]
            )


class WVertex(__Common):

    model = models.Vertex

    @validate(forms.VertexForm)
    def create_or_edit(self, args=[]):
        super(WVertex, self).create_or_edit(*args)

    @login_required(type="JSON")
    @ContentType("text/javascript")
    def list(self, args=[]):
        kwargs = misc.extract_params(self.request)
        start, end = misc.get_slice(self.request)
        qs = self.model.objects.list(**kwargs)
        arr = []
        for vertex in qs:
            _dict = misc.vars(vertex)
            _dict.update(
                dict(
                    objective_id=vertex.get_objective().pk,
                    objective=str(vertex.get_objective()),
                )
            )
            arr.append(_dict)
        self.render({"total": qs.count(), "result": arr})

    @login_required(type="JSON")
    @ContentType("text/javascript")
    def kind_list(self, args=[]):
        self.render([dict(id=cls, name=cls) for cls in self.model.get_subclasses()])

    @login_required(type="JSON")
    @ContentType("text/javascript")
    def objective_list(self, args=[]):
        canonical_name = self.request.REQUEST.get("canonical_name")
        model = misc.evaluate(canonical_name)
        self.render(list(model.objects.objective_list()))


class WEdge(__Common):

    model = models.Edge

    @login_required(type="JSON")
    @ContentType("text/javascript")
    def list(self, args=[]):
        kwargs = misc.extract_params(self.request)
        kwargs["source__active"] = True
        kwargs["target__active"] = True
        start, end = misc.get_slice(self.request)
        qs = self.model.objects.filter(**kwargs)
        arr = [
            dict(
                slug=edge.slug,
                source=edge.source.pk,
                target=edge.target.pk,
                target_name=edge.target.name,
                edge_hash=edge.edge_hash,
            )
            for edge in qs
        ]
        self.render(dict(total=qs.count(), result=arr))

    @validate(forms.EdgeForm)
    def create_or_edit(self, args=[]):
        super(WEdge, self).create_or_edit(*args)

    @login_required(type="JSON")
    @validate(forms.RemoveEdgeForm)
    @ContentType("text/javascript")
    def delete(self, args=[]):
        response = dict(success=False, msg="Não foi possível realizar a operação!")
        try:
            edge = self.model.objects.get(edge_hash=self.request.data.get("edge_hash"))
            edge.delete()
        except Exception as e:
            self.log.error(e)
            response["msg"] += "<br/>%s" % e
        else:
            response = dict(success=True, msg="Realizado com sucesso.")
        self.render(response)
