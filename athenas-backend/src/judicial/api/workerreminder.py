# -*- coding: utf-8 -*-
from contrib.newrest import Restful
from contrib.utils import getLogger
from contrib.utils import DateUtils, employee_from_user
from contrib.nil import nil_pk, nil_unicode, nil_datetime, nil_display
from django.db.models import Q
from judicial.models import WorkerReminder

# from judicial.models import PartLawsuit
# from rh.models import Pessoa

log = getLogger(__name__)


class EJudWorkerReminder(Restful):

    _model = WorkerReminder

    full_text_index = (
        "part__lawsuit__cache_number__icontains",
        "part__lawsuit__origin__interessado__nome__icontains",
    )

    def get_query(self):
        employer = employee_from_user(self.request.user)
        return (
            super(EJudWorkerReminder, self)
            .get_query()
            .filter(Q(Q(receiver=employer) | Q(created_by=self.request.user)))
        )

    def new_object(self, args=[]):
        rst = {"success": False, "message": "nada foi feito ainda!"}

        try:
            params = {}
            for key in list(self.request.POST.keys()):
                value = self.request.POST.getlist(key)
                if len(value) > 1:
                    params.update({key: value})
                else:
                    params.update({key: value[0]})

            if not params.get("receiver", 0):
                raise Exception("É necessário informar o(s) destinatário(s).")

            if not params.get("parts", 0):
                raise Exception("É necessário informar o(s) documentos(s).")

            if not params.get("priority", 0):
                raise Exception("É necessário informar a prioridade.")

            if not params.get("observation"):
                params.update(observation="")

            if "deadline" in params:
                if params.get("deadline") != "":
                    params.update(
                        deadline=DateUtils.str_to_date(params.get("deadline"))
                    )
                else:
                    params.update(deadline=None)

            WorkerReminder.delivery(**params)

        except Exception as e:
            rst.update(message=str(e))
        else:

            rst.update(success=True, message="Comunicação criada com sucesso!")
        self.renderer(rst)

    def resolve(self, args=[]):
        rst = {"sucess": False, "message": "Nada foi feito."}

        try:
            workerreminders = self.get_query().filter(pk__in=args)
            for worker in workerreminders:
                worker.check_resolved()

        except self.Model.DoesNotExist:
            rst.update(message="Comunicado não encontrado.")
        except Exception as e:
            rst.update(message=str(e))

        else:
            rst.update(success=True)

        return self.renderer(rst)

    def renderer_document(self, args=[]):
        rst = {
            "success": False,
            "message": "nada foi feito ainda",
            "document": {
                "content": "Sem informações",
            },
        }
        try:
            log.debug(self.request.GET.get("pk"))
            workerreminder = self.get_query().get(pk=self.request.GET.get("pk"))
        except WorkerReminder.DoesNotExist:
            rst.update(message="Documento não encontrado.")
        except Exception:
            rst.update(message="Error buscando o procedimento. Acesso negado.")
        else:
            rst.update(
                message="Documento exibido.",
                success=True,
                document={
                    "hasContent": True if workerreminder.observation else False,
                    "content": workerreminder.rendered,
                    "appends": workerreminder.rendered_appends,
                },
            )

        self.renderer(rst)

    def model_to_dict(self, instance):
        rst = Restful.model_to_dict(self, instance)
        rst.update(
            status="Concluído" if instance.resolved else "Pendente",
            resolved=(True if instance.resolved else False),
            part=nil_pk(instance.part, None),
            part_unicode=nil_unicode(instance.part, None),
            receiver=nil_pk(instance.receiver, None),
            receiver_unicode=nil_unicode(instance.receiver.pessoa_fisica.nome, None),
            deadline=nil_datetime(instance.deadline, None),
            lawsuit_cache_number=instance.part.lawsuit.cache_number,
            lawsuit=nil_pk(instance.part.lawsuit, None),
            priority=instance.priority,
            priority_display=nil_display(instance, "priority", None),
            solicited_by=instance.solicited_by,
            created_at=nil_datetime(instance.created_at, None),
            resolved_at=nil_datetime(instance.resolved_at, None),
            resolved_by_unicode=instance.resolved_by_unicode,
        )

        return rst

    def entrybox(self, args=[]):
        rst = {
            "success": False,
            "count": 0,
            "message": "nada feito ainda",
            "collection": [],
        }

        try:
            query = self.entry_query()

            if len(args) == 0:

                if "filter" in self.request.GET:
                    query = self.do_filter(query)
                if "keyword" in self.request.GET:
                    query = self.do_full_text_filter(query)
                if "sort" in self.request.GET:
                    query = self.do_sort(query)

                rst.update(count=query.count())
                query = self.do_page(query)

                rst.update(
                    success=True,
                    message="dados carregados com sucesso",
                    collection=[self.model_to_dict(lw) for lw in query],
                )
            else:
                inst = query.get(pk=args[0])

                rst.update(success=True, instance=self.model_to_dict(inst))

        except Exception as e:
            rst.update(message=str(e))

        renderer = self.get_renderer("text/javascript")
        renderer(rst)

    def entry_query(self):
        employer = employee_from_user(self.request.user)

        return self.Model.objects.filter(receiver=employer)

    def outbox(self, args=[]):
        rst = {
            "success": False,
            "count": 0,
            "message": "nada feito ainda",
            "collection": [],
        }

        try:
            query = self.out_query()

            if len(args) == 0:

                if "filter" in self.request.GET:
                    query = self.do_filter(query)
                if "keyword" in self.request.GET:
                    query = self.do_full_text_filter(query)
                if "sort" in self.request.GET:
                    query = self.do_sort(query)

                rst.update(count=query.count())
                query = self.do_page(query)

                rst.update(
                    success=True,
                    message="dados carregados com sucesso",
                    collection=[self.model_to_dict(lw) for lw in query],
                )
            else:
                inst = query.get(pk=args[0])

                rst.update(success=True, instance=self.model_to_dict(inst))

        except Exception as e:
            rst.update(message=str(e))

        renderer = self.get_renderer("text/javascript")
        renderer(rst)

    def out_query(self):

        return self.Model.objects.filter(created_by=self.request.user)
