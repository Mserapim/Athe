# -*- coding:utf-8 -*-
import datetime
import random
import threading
import hashlib

from django.conf import settings
from django.contrib import auth

from django.db import transaction
from django.core.mail import send_mail
from django.template.defaultfilters import slugify
from django import forms

from rh.models import Servidor
from auditoria.models import LineLog
from contrib.crypt import MemoryCipherManager
from contrib.controller import ContentType
from contrib.decorator import login_required, validate
from contrib.extjs import ExtWidget, ExtReportBuild
from contrib.utils import getLogger, person_from_user
from engine.mq.models import Task

from .forms import (
    PollForm,
    ChoiceForm,
    VoteForm,
    DeleteForm,
    PublicationForm,
    CountForm,
    BlockUserForm,
)
from common.poll.models import (
    PollConditions,
    Poll,
    AllowedList,
    BlackList,
    Choice,
    Votes,
    CountedPolls,
    breaker,
)
from common.poll.tasks import fill_allowed_list


log = getLogger(__name__)

# Fallback do modulo transaction entre o django 1.8 e versões anteriores
if not hasattr(transaction, "atomic"):
    transaction.atomic = transaction.commit_on_success


def get_or_instantiate(model, **kwargs):
    """
    Looks like the get_or_create method, but if not found a object returns a new one without save them.
    """
    try:
        obj = model.objects.get(**kwargs)
        created = False
    except model.DoesNotExist:
        obj = model()
        created = True
    finally:
        return obj, created


class VotePolls(ExtWidget):
    @login_required(type="JSON")
    @ContentType("text/javascript")
    def json(self, args=[]):
        self.render("new toolkit.common.poll.VotePolls()")


class SafePolls(ExtWidget):

    @login_required(type="JSON")
    @ContentType("text/javascript")
    def json(self, args=[]):
        self.render("new toolkit.common.poll.Polls()")

    @login_required(type="JSON")
    def all(self, args=[]):
        R = self.request.REQUEST
        rjson = {"total": "0", "result": []}
        now = datetime.datetime.now()

        print("%s" % now.strftime("%d/%m/%Y %H:%M:%S"))

        polls = Poll.objects.filter(active=True).order_by("-id")
        start = int(R.get("start", 0))
        end = int(R.get("limit", 20)) + start

        rjson = {
            "total": polls.count() or "0",
            "result": [
                {
                    "id": poll.id,
                    "title": poll.title,
                    "published": poll.is_published(),
                    "counted": poll.was_counted(),
                    "key": "Chave não pode ser alterada",
                    "updating_allowed_list": poll.updating_allowed_list,
                    "slug": str(slugify(poll.title)),
                    "publication_start": poll.publication_start,
                    "publication_end": poll.publication_end,
                    "locked": poll.is_locked(),
                    "finished": poll.is_finished(),
                    "max_of_choices": poll.max_of_choices,
                    "target": [
                        {"id": condition.id, "description": condition.description}
                        for condition in poll.conditions.all()
                    ],
                }
                for poll in polls[start:end]
            ],
        }
        self.render(rjson)

    @login_required(type="JSON")
    def get(self, args=[]):
        R = self.request.REQUEST
        user = self.request.user
        start = int(R.get("start", 0))
        end = int(R.get("limit", 20)) + start

        kwargs = dict(active=True)

        def checker(poll, user):
            return poll.can_vote_by(user) and poll.is_valid()

        if int(R.get("finished", 0)) == 1:

            def checker(poll, user):
                return poll.can_vote_by(user) and poll.is_valid() and poll.is_finished()

            log.info("POLL: Listing finished polls")
        else:
            now = datetime.datetime.now()
            kwargs["publication_start__lte"] = now
            kwargs["publication_end__gte"] = now

            def checker(poll, user):
                return (
                    poll.can_vote_by(user)
                    and poll.is_valid()
                    and not poll.was_voted_by(user)
                )

            log.info("POLL: Listing on going polls. params => %s" % kwargs)

        polls = Poll.objects.filter(**kwargs).order_by("-id")
        log.info("POLL: qs => %s" % polls)
        result = [
            {
                "id": poll.id,
                "title": poll.title,
                "published": poll.is_published(),
                "locked": poll.is_locked(),
                "publication_start": poll.publication_start,
                "publication_end": poll.publication_end,
                "slug": str(slugify(poll.title)),
                "voted": poll.was_voted_by(user),
                "finished": poll.is_finished(),
                "max_of_choices": poll.max_of_choices,
                "target": [
                    {"id": condition.id, "description": condition.description}
                    for condition in poll.conditions.all()
                ],
                "choices": [
                    {"id": choice.id, "choice": choice.choice}
                    for choice in poll.choices.filter(active=True, meta=False).order_by(
                        "choice"
                    )
                ],
            }
            for poll in polls[start:end]
            if checker(poll, user)
        ]

        log.info("POLL: result => %s" % result)

        self.render({"total": len(result) or "0", "result": result})

    @login_required(type="JSON")
    def conditions(self, args=[]):
        R = self.request.REQUEST
        conds = []
        if "poll" in R:
            conds = PollConditions.objects.filter(polls=R["poll"]).order_by(
                "-description"
            )
        else:
            log.info("Poll conditions action")
            conds = PollConditions.objects.all().order_by("-description")
        start = int(R.get("start", 0))
        end = int(R.get("limit", 20)) + start

        options = [{"id": c.id, "description": c.description} for c in conds[start:end]]
        self.render(options)

    @login_required(type="JSON")
    def choices(self, args=[]):
        R = self.request.REQUEST
        rjson = {"total": "0", "result": []}
        if "poll" in R:
            choices = Choice.objects.filter(
                active=True, meta=False, poll=R["poll"]
            ).order_by("choice")
            start = int(R.get("start", 0))
            end = int(R.get("limit", 20)) + start

            rjson = {
                "total": choices.count() or "0",
                "result": [
                    {"id": c.id, "choice": c.choice, "locked": c.poll.is_locked()}
                    for c in choices[start:end]
                ],
            }
        self.render(rjson)

    @login_required(type="JSON")
    def users(self, args=[]):
        R = self.request.REQUEST
        rjson = {"total": 0, "result": []}
        if "query" in R and R["query"]:
            qs = Servidor.objects.filter(pessoa_fisica__nome__icontains=R["query"])
            rjson = {
                "total": len(qs),
                "result": [
                    {"id": i.user.id, "fullname": i.pessoa_fisica.nome}
                    for i in qs
                    if i.user
                ],
            }
        self.render(rjson)

    @login_required(type="JSON")
    def blocked_users(self, args=[]):
        R = self.request.REQUEST
        rjson = {"total": "0", "result": []}
        if "poll" in R:
            black_list = BlackList.objects.filter(poll=R["poll"])
            if black_list.exists():
                black_list = black_list[0]

                users = black_list.blocked_users.all().order_by("username")
                start = int(R.get("start", 0))
                end = int(R.get("limit", 20)) + start

                rjson = {
                    "total": users.count() or "0",
                    "result": [
                        {
                            "id": user.id,
                            "username": user.username,
                            "email": user.email,
                            "fullname": (
                                person_from_user(user, False).nome
                                if person_from_user(user, False)
                                else ""
                            ),
                        }
                        for user in users[start:end]
                    ],
                }
        self.render(rjson)

    @login_required(type="JSON")
    @validate(BlockUserForm)
    def block_user(self, args=[]):
        rjson = {"success": False, "msg": "Não foi possível realizar a operação."}
        linelog = LineLog(request=self.request, level=3010, status=0)
        vals = self.request.data

        try:
            poll = Poll.objects.get(id=vals["poll"])
            breaker(poll)
            black_list = BlackList.objects.get(poll=poll)
            user = auth.models.User.objects.get(id=vals["user"])

            with transaction.atomic():
                black_list.blocked_users.add(user)

        except Exception as e:
            log.exception(e)
            rjson["msg"] = "%s<br/>%s" % (rjson["msg"], e)
        else:
            rjson = {"success": True, "msg": "Realizado com sucesso."}
            linelog.status = 1

        linelog.save()

        self.render(rjson)

    @login_required(type="JSON")
    @validate(DeleteForm)
    def delete(self, args=[]):
        rjson = {"success": False, "msg": "Não foi possível realizar a operação."}
        linelog = LineLog(request=self.request, status=0)
        vals = self.request.data
        kind = {"Poll": 3003, "Choice": 3006, "User": 3011}
        try:
            if vals["model"] not in kind:
                raise Exception("Tipo de dada inválido!")

            linelog.level = kind[vals["model"]]

            with transaction.atomic():
                if vals["model"] == "User":
                    poll = Poll.objects.get(id=vals["poll"])
                    breaker(poll)
                    black_list = BlackList.objects.get(poll=vals["poll"])
                    user = auth.models.User.objects.get(id=vals["id"])
                    qs = black_list.blocked_users.filter(id=user.id)

                    if qs.exists():
                        black_list.blocked_users.remove(user)
                else:
                    obj = eval(vals["model"]).objects.get(id=vals["id"])
                    obj.active = False
                    obj.save()

        except Exception as e:
            log.exception(e)
            rjson["msg"] = "%s<br/>%s" % (rjson["msg"], e)
        else:
            rjson = {"success": True, "msg": "Realizado com sucesso."}
            linelog.status = 1

        linelog.save()

        self.render(rjson)

    @login_required(type="JSON")
    @validate(PollForm)
    def add_or_edit(self, args=[]):
        rjson = {"success": False, "msg": "Não foi possível realizar a operação."}
        linelog = LineLog(request=self.request, level=3001, status=0)
        vals = self.request.data
        task_uuid = None

        try:
            log.info(
                "=============================================================================="
            )
            poll, created = get_or_instantiate(Poll, id=vals["id"])

            if not created:
                linelog.level = 3002

            if vals["key"] != vals["confirm_key"]:
                raise Exception("A confirmação de chave divergente!")

            poll.title = vals["title"].replace("\n", "")
            poll.max_of_choices = vals["max_of_choices"]

            with transaction.atomic():
                poll.save()
                keypass = hashlib.md5(poll.create_date.ctime().encode()).hexdigest()

                MemoryCipherManager.config(secret_part=vals["key"]).instance(
                    "poll-%s" % poll.id, keypass
                )

                qs = PollConditions.objects.filter(id=vals["target"])
                if (
                    qs.exists()
                    and not poll.conditions.filter(id=vals["target"]).exists()
                ):
                    poll.conditions.clear()
                    poll.conditions.add(qs.latest("id"))
                    poll.updating_allowed_list = True  # Controle para solicitar a criação/atualização da lista de permitidos
                    poll.save()

                poll.test_user_conditions_expressions()

                qs = poll.choices.filter(
                    meta=True, active=True, choice__in=["BRANCO", "NULO"]
                )
                if not qs.exists():
                    Choice(choice="NULO", meta=True, poll=poll).save()
                    Choice(choice="BRANCO", meta=True, poll=poll).save()

                qs = BlackList.objects.filter(poll=poll)
                if not qs.exists():
                    BlackList(poll=poll).save()

                qs = AllowedList.objects.filter(poll=poll)
                if not qs.exists():
                    AllowedList(poll=poll).save()

            if poll.updating_allowed_list:  # Populando lista de permitidos
                task_uuid = Task.start(fill_allowed_list, poll_id=poll.pk).uuid

        except Exception as e:
            log.exception(e)
            rjson["msg"] = "%s<br/>%s" % (rjson["msg"], e)
        else:
            rjson = {
                "success": True,
                "msg": "Realizado com sucesso.",
                "task_uuid": task_uuid,
            }
            linelog.status = 1

        log.info(
            "=============================================================================="
        )
        linelog.json_description["post"]["key"] = "***"
        linelog.json_description["post"]["confirm_key"] = "***"
        linelog.save()

        self.render(rjson)

    @login_required(type="JSON")
    def update_allowed_list(self, args=[]):
        message = dict(success=False, msg="Não foi possível atualizar lista de aptos")
        if args:
            try:
                poll = Poll.objects.get(pk=args[0])
                poll.updating_allowed_list = True
                with transaction.atomic():
                    poll.save()
                    uuid = Task.start(fill_allowed_list, poll_id=poll.pk).uuid
                    message = dict(
                        success=True, msg="Atualizando lista de aptos.", task_uuid=uuid
                    )
            except Exception as e:
                log.exception(e)
                # message.update(msg=e)
        self.render(message)

    @login_required(type="JSON")
    def check_task(self, args=[]):
        message = dict(success=False)
        if args:
            t = Task.objects.get(uuid=args[0])
            message.update(success=bool("ready" in t.state))
        self.render(message)

    @login_required(type="JSON")
    @validate(ChoiceForm)
    def add_or_edit_choice(self, args=[]):
        rjson = {"success": False, "msg": "Não foi possível realizar a operação."}
        linelog = LineLog(request=self.request, level=3004, status=0)
        vals = self.request.data

        try:
            poll = Poll.objects.get(id=vals["poll"])

            choice, created = get_or_instantiate(Choice, id=vals["id"])

            if not created:
                linelog.level = 3005

            choice.choice = vals["choice"].replace("\n", "")
            choice.poll = poll

            with transaction.atomic():
                choice.save()

        except Exception as e:
            log.exception(e)
            rjson["msg"] = "%s<br/>%s" % (rjson["msg"], e)
        else:
            rjson = {"success": True, "msg": "Realizado com sucesso."}
            linelog.status = 1

        linelog.save()

        self.render(rjson)

    @login_required(type="JSON")
    @validate(PublicationForm)
    def publication(self, args=[]):
        rjson = {"success": False, "msg": "Não foi possível realizar a operação."}
        linelog = LineLog(request=self.request, level=3007, status=0)
        vals = self.request.data

        try:
            log.info(
                "=============================================================================="
            )
            if vals["start"] > vals["end"]:
                raise Exception(
                    "A data e hora de inicio não pode ser maior que a data e hora fim!"
                )

            poll = Poll.objects.get(id=vals["poll"])

            if not poll.is_valid():
                raise Exception(
                    "Esta votação não pode ser publicada, o número de opções de voto cadastradas é inferior \
                    ou igual a quantidade máxima de voto por pessoa."
                )

            poll.publication_start = vals["start"]
            date, time = vals["end"].date(), vals["end"].time()
            poll.publication_end = datetime.datetime.combine(
                date, datetime.time(time.hour, time.minute, 59)
            )

            with transaction.atomic():
                poll.save()

        except Exception as e:
            log.exception(e)
            rjson["msg"] = "%s<br/>%s" % (rjson["msg"], e)
        else:
            rjson = {"success": True, "msg": "Realizado com sucesso."}
            linelog.status = 1
        log.info(
            "=============================================================================="
        )

        linelog.save()

        self.render(rjson)

    @login_required(type="JSON")
    @validate(VoteForm)
    def vote(self, args=[]):
        rjson = {"success": False, "msg": "Não foi possível realizar a operação."}

        linelog = LineLog(request=self.request, level=3008, status=0)
        vals = self.request.data

        try:
            log.info(
                "=============================================================================="
            )

            poll = Poll.objects.get(id=vals["poll"])
            if not auth.authenticate(
                username=self.request.user.username, password=vals["password"]
            ):
                raise Exception("Sua senha para confirmação de voto não confere.")
            if not poll.is_on():
                raise Exception("Votação fora do periodo de atividade!")
            if not poll.can_vote_by(self.request.user):
                raise Exception("Você não pode participar dessa votação!")
            if poll.users_who_voted.filter(
                username=self.request.user.username
            ).exists():
                raise Exception("Você já participou desta votação!")

            votes = vals.get("votes") or []
            if votes:
                votes = votes.split(",")

            checked_votes = []
            for vote in votes:
                if vote in checked_votes:
                    raise Exception("Voto duplicado, operação abortada!")
                checked_votes.append(vote)

            choices = []
            if votes and votes[0] == "NULO" or len(votes) > poll.max_of_choices:
                choices.append(poll.choices.get(meta=True, choice="NULO"))
            else:
                if len(votes) < poll.max_of_choices:
                    count = poll.max_of_choices - len(votes)
                    for i in range(count):
                        choices.append(poll.choices.get(meta=True, choice="BRANCO"))

                if len(votes) > 0:
                    qs = poll.choices.filter(meta=False, id__in=votes)
                    if qs.count() != len(votes):
                        raise Exception("Opções de voto inválidas!")
                    for choice in qs:
                        choices.append(choice)

            with transaction.atomic():
                for choice in choices:
                    vote = Votes(poll=poll, choice=choice)
                    vote.save()
                    keypass = hashlib.md5(poll.create_date.ctime().encode()).hexdigest()

                    vote.signature = (
                        MemoryCipherManager.instance("poll-%s" % poll.id, keypass)
                        .encrypt("%s|%s|%s" % (vote.id, poll.id, choice.id))
                        .decode()
                    )

                    vote.save()
                    log.info("sign: %s" % vote.signature)

                poll.users_who_voted.add(self.request.user)

            send_async_email = threading.Thread(
                target=self.send_email,
                args=(
                    "Confirmação de voto",
                    """
                O seu voto para eleição "%s" foi computado com sucesso.\n\n
                Este é um email automático gerado pelo sistema de votaçao, não responda-o. \n\n
                Ministério Público do Estado do Tocantins
                """
                    % poll.title,
                    "votacao@mpto.mp.br",
                    [self.request.user.email],
                ),
            )

            send_async_email.start()

        except Exception as e:
            log.exception(e)
            rjson["msg"] = "%s<br/>%s" % (rjson["msg"], e)
        else:
            rjson = {"success": True, "msg": "Realizado com sucesso."}
            linelog.status = 1
        log.info(
            "=============================================================================="
        )

        linelog.json_description["post"]["votes"] = "***"
        linelog.json_description["post"]["password"] = "***"
        linelog.save()

        self.render(rjson)

    def send_email(self, *args):
        try:
            send_mail(*args)
            log.info("Confirmation email sent")
        except Exception as e:
            log.error("Confirmation email not sent %s" % e)

    @login_required(type="JSON")
    @validate(CountForm)
    def count(self, args=[]):
        rjson = {"success": False, "msg": "Não foi possível realizar a operação."}

        linelog = LineLog(request=self.request, level=3009, status=0)
        vals = self.request.data

        try:
            # log.info('==============================================================================')
            poll = Poll.objects.get(id=vals["poll"])
            keypass = hashlib.md5(poll.create_date.ctime().encode()).hexdigest()
            cipher = MemoryCipherManager.instance("poll-%s" % poll.id, keypass)
            if vals["key"] != cipher.secret_part:
                raise Exception("Chave de segurança incorreta!")

            votes = Votes.objects.filter(poll=poll)

            with transaction.atomic():
                for vote in votes:
                    plain = cipher.decrypt(vote.signature).decode()
                    proof = "%s|%s|%s" % (vote.id, vote.poll.id, vote.choice.id)

                    if plain == proof:
                        vote.authentic = True
                        log.info("Poll# authentic vote %s == %s " % (plain, proof))
                    else:
                        vote.authentic = False
                        log.info("Poll# not authentic vote %s != %s " % (plain, proof))

                    vote.counted = True
                    vote.save()

                qs = CountedPolls.objects.filter(poll=poll)
                if not qs.exists():
                    CountedPolls(poll=poll).save()

            # authentic_votes = Votes.objects.filter(poll=poll, counted=True, authentic=True)
            # authentic_votes = Votes.objects.filter(poll=poll, authentic=True)
            # white_total = authentic_votes.filter(choice=poll.choices.get(meta=True, choice='BRANCO')).count()
            # null_total = authentic_votes.filter(choice=poll.choices.get(meta=True, choice='NULO')).count()
            # valid_votes = authentic_votes.count() - (white_total + null_total)

            # vote_forms = (valid_votes + white_total + (null_total * poll.max_of_choices)) / poll.max_of_choices

            # # voters = poll.users_who_voted.all().count()

            # result = []
            # choices = poll.choices.filter(meta=False, active=True)
            # def percentage(choice_total):
            #     return round(((100 * float(choice_total)) / authentic_votes.count()), 1) if authentic_votes.count() > 0 else 0
            # for choice in choices:
            #     choice_total = authentic_votes.filter(choice=choice).count()
            #     percent = percentage(authentic_votes.filter(choice=choice).count())
            #     result.append({'label': choice.choice, 'value': '%s votos - %s%%' % (choice_total, percent)})
            # result.append({'label': 'BRANCOS', 'value': '%s votos - %s%%' % (white_total, percentage(white_total))})
            # result.append({'label': 'NULOS', 'value': '%s votos - %s%%' % (null_total, percentage(null_total))})
            # result.append({'label': 'Votos válidos', 'value': valid_votes or '0'})
            # result.append({'label': 'Votantes', 'value': vote_forms or '0'})

            # log.info('==============================================================================')
            # log.info('==============================================================================')
            # log.info(result)
            # log.info('==============================================================================')
            # log.info('==============================================================================')
        except Exception as e:
            log.exception(e)
            rjson["msg"] = "%s<br/>%s" % (rjson["msg"], e)
        else:
            # rjson = {'success': True, 'msg': 'Realizado com sucesso. Aguarde notificação de conclusão do relatório', 'data': result}

            rjson = {"success": True, "msg": "Realizado com sucesso."}
            linelog.status = 1
            # linelog.json_description['post']['key'] = cipher.secret

        linelog.save()

        self.render(rjson)

    def test(self, args=[]):

        if settings.DEBUG:
            poll = Poll.objects.filter(active=True).latest("id")
            choices = poll.choices.filter(active=True, meta=False).values("id")
            users = auth.models.User.objects.filter(
                username__in=[
                    "tonyreis",
                    "leonardomata",
                    "rodrigomatias",
                    "huancarlos",
                    "fernandopinto",
                    "marciliobrasileiro",
                    "gustavodettenborn",
                    "raysonsilva",
                ]
            )

            for user in users:
                votes = []
                limit = random.randint(0, poll.max_of_choices + 1)
                for i in range(limit):
                    votes.append(str(random.choice(choices)["id"]))
                print(
                    "========================================================================="
                )

                params = {"poll": poll.id, "votes": ",".join(votes), "password": "123"}
                print("Voting %s" % params)
                self.request.POST = params
                self.request.data = params
                authenticated = auth.authenticate(
                    username=user.username, password="123"
                )
                auth.login(self.request, authenticated)
                try:
                    response = self.vote()
                except Exception as e:
                    log.exception(e)
                else:
                    print("Response: %s" % response)


class SafePollReport(ExtReportBuild):

    from django import forms

    report_src = "/to/mpe/votacao/extratoeleicao/resultado_votacao"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/votacao/extratoeleicao/",
        }
    ]

    def get_generated_filename(self):
        filename = ""
        try:
            poll = Poll.objects.get(active=True, pk=self.request.REQUEST.get("poll"))
        except Exception as e:
            filename = "votacao-indisponivel"
            log.exception(e)
        else:
            filename = "resultado-%(poll)s" % {"poll": poll.title}
        return "%s.pdf" % slugify(filename)

    class Form(forms.Form):
        poll = forms.CharField()


class SafePollNonVotersReport(ExtReportBuild):

    from django import forms

    report_src = "/to/mpe/votacao/extratonaovotante/resultado_votacao"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/votacao/extratonaovotante/",
        }
    ]

    def get_generated_filename(self):
        raise Exception("Operação não permitida!")

        filename = ""
        try:
            poll = Poll.objects.get(active=True, pk=self.request.REQUEST.get("poll"))
        except Exception as e:
            filename = "indisponivel"
            log.exception(e)
        else:
            filename = "resultado-parcial-de-não-votantes-de-%(poll)s" % {
                "poll": poll.title
            }
        return "%s.pdf" % slugify(filename)

    class Form(forms.Form):
        poll = forms.CharField()


class SafePollSimpleReport(ExtReportBuild):
    report_src = "/to/mpe/votacao/extratoeleicaofinal/resultado_votacao"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/votacao/extratoeleicaofinal/",
        }
    ]

    def get_generated_filename(self):
        filename = ""
        try:
            poll = Poll.objects.get(active=True, pk=self.request.REQUEST.get("poll"))
        except Exception as e:
            filename = "votacao-indisponivel"
            log.exception(e)
        else:
            filename = "resultado-simplificado-%(poll)s" % {"poll": poll.title}
        return "%s.pdf" % slugify(filename)

    class Form(forms.Form):
        poll = forms.CharField()


class SafePollAbleVoters(ExtReportBuild):
    report_src = "/to/mpe/votacao/extratoaptos/resultado_votacao"

    params = [
        {
            "nome": "SUBREPORT_DIR",
            "tipo": "String",
            "valor": "to/mpe/votacao/extratoaptos/",
        }
    ]

    def get_generated_filename(self):
        filename = ""
        try:
            poll = Poll.objects.get(active=True, pk=self.request.REQUEST.get("poll"))
        except Exception as e:
            filename = "relatorio-de-usuarios-aptos-indisponivel"
            log.exception(e)
        else:
            filename = "relatorio-de-usuarios-aptos-%(poll)s" % {"poll": poll.title}
        return "%s.pdf" % slugify(filename)

    class Form(forms.Form):
        poll = forms.CharField()
