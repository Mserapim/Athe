# -*- coding:utf-8 -*-
import base64
import hashlib
import json
import os
import random

from django.db import transaction
from django.db.models import Q

from contrib.controller import JsonResponseController
from contrib.decorator import is_public, login_required
from contrib.helpers import err2dict
from contrib.middleware import set_current_user
from contrib.utils import getLogger
from edocs.protocolo.models import Attachment
from edocs.protocolo.models import Lotacao as Workplace
from edocs.protocolo.models import Protocolo as Entry
from edocs.protocolo.models import TipoDocumento as DocType
from ged.models import Arquivo as File
from judicial.models import (
    Attached,
    Manifestation,
    OutCourtLawsuit,
    PartLawsuit,
    RequestExternalAccess,
)
from judicial.rpc.forms import (
    EntryForm,
    ManifestationAttachFile,
    ManifestationForm,
    ManifestationSaveForm,
    PetitionForm,
)
from rh.models import Localidade, Lotacao
from rh.models import PessoaFisica as Individual
from rh.models import PessoaJuridica as LegalPerson
from standard.models import Choice, Configuration
from web.models import RegularWebUser, TokenWebUser
from edocs.protocolo.models import (
    Protocolo as Entry,
    TipoDocumento as DocType,
    Lotacao as Workplace,
    Attachment,
)
from rh.models import (
    Localidade,
    Lotacao,
    PessoaFisica as Individual,
    PessoaJuridica as LegalPerson,
)
from judicial.models import (
    OutCourtLawsuit,
    PartLawsuit,
    Manifestation,
    Attached,
    RequestExternalAccess,
)
from judicial.rpc.forms import (
    EntryForm,
    ManifestationSaveForm,
    ManifestationAttachFile,
    PetitionForm,
)

# Fallback do modulo transaction entre o django 1.8 e versões anteriores
if not hasattr(transaction, "atomic"):
    transaction.atomic = transaction.commit_on_success

log = getLogger()


class LawsuitException(Exception):
    pass


class LawsuitRPC(JsonResponseController):

    def __init__(self, *args, **kwargs):
        super(LawsuitRPC, self).__init__(*args, **kwargs)

        self.cfg = Configuration.get_or_create("ejud")
        self.SIGNED = Q(signed_by__isnull=False, signed_at__isnull=False)

        # if self.response_format == 'json':
        #     self.response['Content-Type'] = 'text/javascript; charset=utf-8'

    @is_public()
    def public_form_options(self, args=[]):
        kind_choices = Choice.get_choices_for("judicial", "TYPE_LAWSUIT")
        years = (
            OutCourtLawsuit.objects.filter(year__isnull=False)
            .values_list("year", flat=True)
            .order_by("-year")
            .distinct()
        )
        cities = (
            Lotacao.objects.filter(nome__icontains="promotoria")
            .values_list("localidade", "localidade__nome")
            .order_by("localidade__nome")
            .distinct()
        )

        response_data = {
            "lawsuit_kinds": [("", "Todos")] + list(kind_choices),
            "lawsuit_years": [("", "Todos")] + [(year, year) for year in years],
            "lawsuit_cities": [("", "Todas")] + list(cities),
        }

        self.render(response_data)

    @is_public()
    def lawsuit_search(self, args=[]):
        response_data = {"success": False, "total": "0", "list": []}

        qs = (
            OutCourtLawsuit.objects.filter(
                removed_at__isnull=True, parts__signed_by__isnull=False
            )
            .distinct()
            .order_by("-year", "-number_lawsuit")
        )

        year = self.request.POST.get("year")
        kind = self.request.POST.get("kind")
        number = self.request.POST.get("number")
        city = self.request.POST.get("city")
        name = self.request.POST.get("name")
        page = int(self.request.POST.get("page") or 1)
        page_items = int(self.request.POST.get("page_items") or 15)

        end = page * page_items
        start = end - page_items

        if year:
            qs = qs.filter(year=year)

        if kind:
            qs = qs.filter(type_lawsuit=kind)

        if city:
            qs = qs.filter(location__localidade=city)

        if number:
            qs = qs.filter(cache_number__icontains=number)

        elif name:
            qs = qs.filter(
                Q(has_interested__person__nome__icontains=name)
                | Q(blokes__person__bloke__nome__icontains=name)
                | Q(blokes__commonperson__bloke__nome__icontains=name)
                | Q(blokes__governmentpublic__bloke__nome__icontains=name)
                | Q(blokes__company__bloke__nome__icontains=name)
                | Q(blokes__governmentpublic__bloke__nome__icontains=name)
            )

        if qs.exists():
            total = qs.count() or "0"
            lawsuits = []
            for lawsuit in qs[start:end]:
                lawsuits.append(
                    {
                        "id": lawsuit.id,
                        "subjects": [str(matter) for matter in lawsuit.matters.all()]
                        or ["Não informado"],
                        "kind": lawsuit.type_lawsuit,
                        "kind_text": lawsuit.get_type_lawsuit_display(),
                        "code": lawsuit.origin.codigo,
                        "number": lawsuit.number_lawsuit,
                        "year": lawsuit.year,
                        "can_read": getattr(
                            lawsuit, "can_read", random.choice([True, False])
                        ),
                        "full_number": lawsuit.cache_number,
                        "location": (
                            str(lawsuit.location)
                            if hasattr(lawsuit, "location")
                            else "Não informado"
                        ),
                        "cities": [str(city) for city in lawsuit.notice_locations.all()]
                        or ["Não informado"],
                        "interested": list(
                            lawsuit.interested.values_list("nome", flat=True)
                        )
                        or ["Não informado"],
                        "investigated": [str(bloke) for bloke in lawsuit.blokes.all()]
                        or ["Não informado"],
                    }
                )

            response_data.update(success=True, total=total, list=lawsuits)

        self.render(response_data)

    @is_public()
    def public_partlawsuit_list(self, args=[]):
        response_data = {"success": False}

        lawsuit_id = self.request.POST.get("lawsuit") or 0

        part_lawsuits = []
        qs = PartLawsuit.objects.filter(self.SIGNED, lawsuit=lawsuit_id).order_by(
            "-created_at"
        )

        for part in qs:
            specialized_part = part.my_origin

            signed_by = "Não informado"
            if hasattr(specialized_part.signed_by, "servidor"):
                signed_by = str(specialized_part.signed_by.servidor.pessoa_fisica)

            part_lawsuits.append(
                {
                    "id": specialized_part.id,
                    "lawsuit": specialized_part.lawsuit.cache_number,
                    "lawsuit_id": specialized_part.lawsuit.id,
                    "title": specialized_part.title,
                    "kind": specialized_part.type_part,
                    "is_public": specialized_part.is_public,
                    "can_read": specialized_part.can_read,
                    "created_at": specialized_part.created_at,
                    "signed": specialized_part.signed,
                    "signed_by": signed_by,
                    "event": (
                        specialized_part.event_control.number_control
                        if specialized_part.event_control
                        else "-"
                    ),
                }
            )

        response_data.update(success=True, list=part_lawsuits)

        self.render(response_data)

    @is_public()
    def public_partlawsuit_doc(self, args=[]):
        response_data = {"success": False}

        part_lawsuit_id = self.request.POST.get("id") or 0

        part = PartLawsuit.objects.filter(self.SIGNED, id=part_lawsuit_id).first()

        part_lawsuit_document = {}

        if part:
            specialized_part = part.my_origin
            extra_pages = specialized_part.extra_pages or []
            part_lawsuit_document = {
                "id": specialized_part.id,
                "is_public": specialized_part.is_public,
                "markup": base64.b64encode(specialized_part.rendered.encode()).decode(),
                "extra_pages": [
                    base64.b64encode(page.encode()).decode()
                    for page in extra_pages
                    if page
                ],
            }
        response_data.update(success=True, obj=part_lawsuit_document)

        self.render(response_data)

    @login_required(type="JSON")
    def __check_user(self):
        username = self.request.POST.get("username")
        password = self.request.POST.get("password")
        if not password:
            return TokenWebUser.objects.filter(token=username).first()
        return RegularWebUser.authenticate(username, password)

    @login_required(type="JSON")
    def form_options(self, args=[]):
        doctype_ids = json.loads(self.cfg.get("autoCreateFor"))
        qs_cities = Localidade.objects.filter(estado__sigla="TO").order_by("nome")
        response_data = {
            "doctypes": [
                {"value": doc.id, "text": doc.nome}
                for doc in DocType.objects.filter(pk__in=doctype_ids)
            ],
            "cities": [{"value": city.id, "text": city.nome} for city in qs_cities],
        }
        self.render(response_data)

    @login_required(type="JSON")
    def create(self, args=[]):
        response_data = {"success": False}
        user = self.__check_user()
        if user:
            form = EntryForm(self.request.POST)

            if form.is_valid():
                form_data = form.cleaned_data
                try:

                    workplace_id = form_data.get("workplace")
                    if not workplace_id:
                        workplace_id = int(self.cfg.get("mainTriageCenter", 0)) or None

                        if not workplace_id:
                            raise Exception(
                                "Não foi definido um centro de triagem principal"
                            )

                    workplace = Workplace.objects.get(pk=workplace_id)

                    set_current_user(workplace.responsavel.user)

                    entry = Entry(
                        interessado=user.person,
                        tipo_documento=DocType.objects.get(pk=form_data["doc_type"]),
                        assunto=form_data["subject"],
                        resumo=form_data["story"],
                        orgao_geral_origem=workplace.orgaogeral_ptr,
                        servidor_origem=workplace.responsavel,
                    )

                    entry._signed_by_web = True

                    with transaction.atomic():

                        entry.save()

                        move = entry.movimentacoes.get(passo=0)
                        entry._current_moviment = move

                        for name, upfile in list(self.request.FILES.items()):
                            title = self.request.POST.get(
                                "file_name_%s" % name.split("_")[-1], upfile.name
                            )

                            attach = Attachment(
                                title=title,
                                moviment=move,
                                attach=self.__create_ged(upfile),
                            )
                            attach.save()

                        move.do_send(
                            location_destination=[workplace.pk],
                            employee_origin=workplace.responsavel,
                        )
                except Exception as e:
                    log.exception(e)
                    log.error(e)
                    response_data.update(
                        message="Não foi possível criar notícia de fato."
                    )
                else:
                    response_data.update(
                        success=True,
                        message="Notícia de fato criada. Guarde o protocolo %s"
                        % entry.codigo,
                    )
            else:
                response_data.update(
                    message="Preencha o formulário corretamente.", errors=err2dict(form)
                )
        else:
            response_data.update(message="Usuário ou token inválido.")
        self.render(response_data)

    @login_required(type="JSON")
    def lawsuit_list(self, args=[]):
        response_data = {"success": False}
        user = self.__check_user()
        if user:
            lawsuits = []
            qs = OutCourtLawsuit.objects.filter(
                Q(origin__interessado=user.person)
                | Q(has_interested__person=user.person)
            ).order_by("-year", "-number_lawsuit")
            for lawsuit in qs:
                lawsuits.append(
                    {
                        "id": lawsuit.id,
                        "title": lawsuit.title or lawsuit.origin.assunto,
                        "kind": lawsuit.type_lawsuit,
                        "kind_text": lawsuit.get_type_lawsuit_display(),
                        # 'text': base64.b64encode(lawsuit.origin.resumo),
                        "code": lawsuit.origin.codigo,
                        "number": lawsuit.number_lawsuit,
                        "year": lawsuit.year,
                        "full_number": lawsuit.cache_number,
                    }
                )
            response_data.update(success=True, list=lawsuits)
        else:
            response_data.update(message="Usuário ou token inválido.")
        self.render(response_data)

    @login_required(type="JSON")
    def lawsuit_attachs(self, args=[]):
        response_data = {"success": False}
        user = self.__check_user()

        if user:
            lawsuit_id = self.request.POST.get("lawsuit") or 0
            attachs = []

            qs = Attachment.objects.filter(
                protocol__interessado=user.person,
                protocol__out_court_lawsuits=lawsuit_id,
            )

            for a in qs:
                attachs.append(
                    {"id": a.id, "title": a.title, "url": a.attach.permalink()}
                )
            response_data.update(success=True, list=attachs)
        else:
            response_data.update(message="Usuário ou token inválido.")
        self.render(response_data)

    @login_required(type="JSON")
    def partlawsuit_list(self, args=[]):
        response_data = {"success": False}
        user = self.__check_user()
        if user:
            lawsuit_id = self.request.POST.get("lawsuit") or 0

            part_lawsuits = []
            qs = PartLawsuit.objects.filter(
                Q(lawsuit__origin__interessado=user.person)
                | Q(lawsuit__has_interested__person=user.person),
                self.SIGNED,
                lawsuit=lawsuit_id,
            )

            auths = RequestExternalAccess.authorizations_by_user(user)
            is_allowed = OutCourtLawsuit.objects.filter(
                parts__in=auths, pk=lawsuit_id
            ).exists()

            for part in qs:
                specialized_part = part.my_origin

                part_has_manifestation = specialized_part.manifestations.filter(
                    Q(who=user.person)
                    | Q(who__in=[a.as_representative_of for a in auths])
                ).exists()

                part_lawsuits.append(
                    {
                        "id": specialized_part.id,
                        "lawsuit": specialized_part.lawsuit.cache_number,
                        "lawsuit_id": specialized_part.lawsuit.id,
                        "title": specialized_part.title,
                        "kind": specialized_part.type_part,
                        "is_public": specialized_part.is_public,
                        "event_number": specialized_part.number_event_control,
                        "has_manifestation": part_has_manifestation,
                        "is_allowed": is_allowed,
                        # 'text': base64.b64encode(specialized_part.cache_rendered),
                        "signed": specialized_part.signed,
                        "cache_size": specialized_part.cache_filestream_size,
                        # 'markup': base64.b64encode(specialized_part.rendered.encode())
                    }
                )
            response_data.update(success=True, list=part_lawsuits)
        else:
            response_data.update(message="Usuário ou token inválido.")
        self.render(response_data)

    @login_required(type="JSON")
    def partlawsuit_get(self, args=[]):
        response_data = {"success": False}
        user = self.__check_user()
        if user:
            part_lawsuit_id = self.request.POST.get("id") or 0

            part = PartLawsuit.objects.filter(
                Q(lawsuit__origin__interessado=user.person)
                | Q(lawsuit__has_interested__person=user.person),
                self.SIGNED,
                id=part_lawsuit_id,
            ).first()

            part_lawsuit_document = {}
            auths = RequestExternalAccess.authorizations_by_user(user)
            is_allowed = part.lawsuit.parts.filter(id__in=auths).exists()

            if part:
                specialized_part = part.my_origin
                extra_pages = specialized_part.extra_pages or []
                part_lawsuit_document = {
                    "id": specialized_part.id,
                    "title": specialized_part.title,
                    "kind": specialized_part.type_part,
                    "is_public": specialized_part.is_public,
                    "is_allowed": is_allowed,
                    # 'text': base64.b64encode(specialized_part.cache_rendered),
                    "signed": specialized_part.signed,
                    "markup": base64.b64encode(
                        specialized_part.rendered.encode()
                    ).decode(),
                    "extra_pages": [
                        base64.b64encode(page.encode()).decode() for page in extra_pages
                    ],
                }
            response_data.update(success=True, obj=part_lawsuit_document)
        else:
            response_data.update(message="Usuário ou token inválido.")
        self.render(response_data)

    @login_required(type="JSON")
    def manifestation_get(self, args=[]):
        response_data = {"success": False}
        user = self.__check_user()
        if user:
            obj = {}
            auths = RequestExternalAccess.authorizations_by_user(user)
            manifest = Manifestation.objects.filter(
                Q(who=user.person) | Q(who__in=[a.as_representative_of for a in auths]),
                id=self.request.POST.get("id"),
            ).first()

            if manifest:
                diligence = None
                if hasattr(manifest, "diligence") and manifest.diligence:

                    attached = None
                    if (
                        hasattr(manifest.diligence, "diligence_file")
                        and manifest.diligence.diligence_file
                    ):
                        attached = {
                            "filename": manifest.diligence.diligence_file.filename,
                            "file": manifest.diligence.diligence_file.file,
                            "url": manifest.diligence.diligence_file.permalink(),
                        }

                    diligence = {
                        "file": attached,
                        "number": manifest.diligence.formated_number,
                        "title": manifest.diligence.title,
                        "observation": manifest.diligence.observation,
                        "deadline": manifest.diligence.deadline,
                    }

                obj = {
                    "id": manifest.id,
                    "part_lawsuit_id": manifest.reference.id,
                    "who": manifest.who.nome,
                    "who_kind_text": manifest.get_who_type_display(),
                    "kind": manifest.manifestation_type,
                    "kind_text": manifest.get_manifestation_type_display(),
                    "deadline": manifest.deadline,
                    "content": base64.b64encode(
                        (manifest.content or "").encode()
                    ).decode(),
                    "markup": base64.b64encode(manifest.renderer.encode()).decode(),
                    "readonly": bool(manifest.read_only),
                    "signed_at": manifest.signed_at,
                    "signed": bool(manifest.signed_at and manifest.signed_by),
                    "diligence": diligence,
                    "outcourtlawsuit": manifest.reference.lawsuit.cache_number,
                    "protocol_origin": manifest.reference.lawsuit.origin.codigo,
                }
            response_data.update(success=True, obj=obj)
        else:
            response_data.update(message="Usuário ou token inválido.")
        self.render(response_data)

    @login_required(type="JSON")
    def manifestation_list(self, args=[]):
        response_data = {"success": False}
        user = self.__check_user()
        if user:

            manifestations = []

            auths = RequestExternalAccess.authorizations_by_user(user)

            qs = Manifestation.objects.filter(
                Q(who=user.person) | Q(who__in=[a.as_representative_of for a in auths])
            )

            if self.request.POST.get("wich") == "todo":
                qs = qs.filter(~self.SIGNED)
            else:
                part_lawsuit_id = self.request.POST.get("part_lawsuit") or 0
                qs = qs.filter(reference=part_lawsuit_id)

            for manifest in qs:

                manifestations.append(
                    {
                        "id": manifest.id,
                        "lawsuit": manifest.reference.lawsuit.cache_number,
                        "part_lawsuit": str(manifest.reference),
                        "part_lawsuit_id": manifest.reference.id,
                        "who": manifest.who.nome,
                        "who_kind_text": manifest.get_who_type_display(),
                        "kind": manifest.manifestation_type,
                        "kind_text": manifest.get_manifestation_type_display(),
                        "deadline": manifest.deadline,
                        # 'content': manifest.content,
                        # 'markup': base64.b64encode(manifest.renderer.encode()),
                        "readonly": bool(manifest.read_only),
                        "signed_at": manifest.signed_at,
                        "signed": bool(manifest.signed_at and manifest.signed_by),
                        # 'diligence': diligence,
                    }
                )
            response_data.update(success=True, list=manifestations)
        else:
            response_data.update(message="Usuário ou token inválido.")
        self.render(response_data)

    @login_required(type="JSON")
    def there_is_manifestations_todo(self, args=[]):
        response_data = {"success": False}
        user = self.__check_user()
        if user:
            auths = RequestExternalAccess.authorizations_by_user(user)
            qs = Manifestation.objects.filter(
                Q(who=user.person) | Q(who__in=[a.as_representative_of for a in auths])
            ).filter(~self.SIGNED, who=user.person)

            response_data.update(success=True, yes=qs.exists())
        else:
            response_data.update(message="Usuário ou token inválido.")
        self.render(response_data)

    @login_required(type="JSON")
    def manifestation_save(self, args=[]):
        response_data = {"success": False}
        user = self.__check_user()
        if user:
            form = ManifestationForm(self.request.POST, self.request.FILES)

            if form.is_valid():
                form_data = form.cleaned_data
                try:
                    auths = RequestExternalAccess.authorizations_by_user(user)

                    manifest = Manifestation.objects.get(
                        Q(who=user.person)
                        | Q(who__in=[a.as_representative_of for a in auths]),
                        pk=form_data["id"],
                    )
                    manifest.content = form_data["content"]

                    with transaction.atomic():
                        manifest.save()

                        upfile = self.request.FILES.get("upload")
                        if upfile:
                            attach = Attached(
                                title=form_data["title"],
                                attached_manifestation=manifest,
                                file_descriptor=self.__create_ged(upfile),
                            )
                            attach.save()

                except Exception as e:
                    self.log.error(e)
                    response_data.update(
                        message="Não foi possível salvar a manifestação."
                    )
                else:
                    response_data.update(success=True, message="Manifestação salva.")
            else:
                response_data.update(
                    message="Preencha o formulário corretamente.", errors=err2dict(form)
                )
        else:
            response_data.update(message="Usuário ou token inválido.")
        self.render(response_data)

    @login_required(type="JSON")
    def manifestation_attachs(self, args=[]):
        response_data = {"success": False}
        user = self.__check_user()
        if user:
            attachs = []
            auths = RequestExternalAccess.authorizations_by_user(user)
            qs = Attached.objects.filter(
                Q(attached_manifestation__who=user.person)
                | Q(
                    attached_manifestation__who__in=[
                        a.as_representative_of for a in auths
                    ]
                ),
                attached_manifestation=self.request.POST.get("id"),
            )

            for attach in qs:
                attachs.append(
                    {
                        "id": attach.id,
                        "title": attach.title,
                        "url": attach.file_descriptor.permalink(),
                    }
                )
            response_data.update(success=True, list=attachs)
        else:
            response_data.update(message="Usuário ou token inválido.")
        self.render(response_data)

    @login_required(type="JSON")
    def manifestation_attach_file(self, args=[]):
        response_data = {"success": False}
        user = self.__check_user()
        if user:
            form = ManifestationAttachFile(self.request.POST, self.request.FILES)
            if form.is_valid():
                form_data = form.cleaned_data
                try:
                    manifest = Manifestation.objects.get(pk=form_data["manifest"])
                    with transaction.atomic():
                        upfile = self.request.FILES["upload"]
                        attach = Attached(
                            title=form_data["title"],
                            attached_manifestation=manifest,
                            file_descriptor=self.__create_ged(upfile),
                        )
                        attach.save()

                except Exception as e:
                    self.log.error(e)
                    response_data.update(message="%s" % e)
                else:
                    response_data.update(success=True, message="Anexo salvo.")
            else:
                response_data.update(
                    message="Preencha corretamente o formulário", errors=err2dict(form)
                )
        else:
            response_data.update(message="Usuário ou token inválido.")
        self.render(response_data)

    @login_required(type="JSON")
    def manifestation_sign(self, args=[]):
        response_data = {"success": False}
        user = self.__check_user()
        if user:
            try:
                auths = RequestExternalAccess.authorizations_by_user(user)
                manisfest = Manifestation.objects.get(
                    Q(who=user.person)
                    | Q(who__in=[a.as_representative_of for a in auths]),
                    pk=self.request.POST.get("id"),
                )
                with transaction.atomic():
                    manisfest.sign(user.person)
            except Exception as e:
                self.log.error(e)
                response_data.update(message="%s" % e)
            else:
                response_data.update(success=True, message="Manifestação assinada.")
        else:
            response_data.update(message="Usuário ou token inválido.")
        self.render(response_data)

    @is_public()
    def petitions_list(self, args=[]):
        response_data = {"success": False}
        user = self.__check_user()
        if user:
            petitions = []
            qs = RequestExternalAccess.objects.filter(person=user.person)
            for petition in qs:

                attach = petition.attaches.all().first()
                if attach:
                    file_descriptor = getattr(attach, "file_descriptor", None)
                    attach = {
                        "title": attach.title,
                        "url": file_descriptor.permalink() if file_descriptor else "",
                    }

                representing = ""
                if hasattr(petition.as_representative_of, "pessoafisica"):
                    individual = petition.as_representative_of.pessoafisica
                    representing = "[%s] %s" % (individual.cpf, individual.nome)

                justifications = [
                    au.justification
                    for au in petition.in_authorization_external_access.all()
                ]

                petitions.append(
                    {
                        "id": petition.id,
                        "lawsuit": petition.lawsuit.cache_number,
                        "person": petition.person.nome,
                        "person_id": petition.person.id,
                        "as_representative_of": representing,
                        "request": petition.request,
                        "authorized_at": petition.authorized_at,
                        "revoked_at": petition.revoked_at,
                        "denied_at": petition.denied_at,
                        "justifications": justifications,
                        "attach": attach,
                        "status": petition.get_state_display(),
                        "created_at": petition.created_at,
                    }
                )

            response_data.update(success=True, list=petitions)
        else:
            response_data.update(message="Usuário ou token inválido.")
        self.render(response_data)

    def __is_involved(self, qs, person):
        q_params = (
            Q(origin__interessado=person)
            | Q(has_interested__person=person)
            | Q(blokes__commonperson__bloke=person)
        )
        if isinstance(person, Individual):
            q_params = (
                q_params
                | Q(blokes__person__bloke=person)
                | Q(blokes__governmentpublic__bloke=person)
            )
        elif isinstance(person, LegalPerson):
            q_params = (
                q_params
                | Q(blokes__association__bloke=person)
                | Q(blokes__company__bloke=person)
            )

        return qs.filter(q_params).exists()

    @login_required(type="JSON")
    def petition_create(self, args=[]):
        response_data = {"success": False}
        user = self.__check_user()
        if user:
            form = PetitionForm(self.request.POST)
            if form.is_valid():
                form_data = form.cleaned_data
                try:
                    qs = OutCourtLawsuit.objects.filter(id=form_data["lawsuit"].id)

                    if not user.is_lawyer_user() and not self.__is_involved(
                        qs, user.person
                    ):
                        raise LawsuitException(
                            "Somente é permitido peticionar sobre um procedimento que você conste como interessado."
                        )

                    elif (
                        user.is_lawyer_user()
                        and form_data["as_representative_of"]
                        and not self.__is_involved(
                            qs, form_data["as_representative_of"]
                        )
                    ):

                        raise LawsuitException(
                            "Somente é permitido peticionar sobre um procedimento que o representado conste como interessado."
                        )

                    petition = RequestExternalAccess(
                        person=user.person,
                        lawsuit=form_data["lawsuit"],
                        as_representative_of=form_data["as_representative_of"],
                        request=form_data["request"],
                    )

                    with transaction.atomic():
                        petition.skip_sign_current_moviment = True
                        petition.save()
                        petition.sign_part()
                        upfile = self.request.FILES.get("upload")
                        if upfile:
                            attach = Attached(
                                title=upfile.name,
                                attached_document=petition,
                                file_descriptor=self.__create_ged(upfile),
                            )
                            attach.skip_read_only_validate = True
                            attach.save()

                except LawsuitException as e:
                    self.log.ex(e)
                    response_data.update(message="%s" % e)
                except Exception as e:
                    self.log.exception(e)
                    response_data.update(
                        message="Não foi possível salvar petição. %s" % e
                    )
                else:
                    response_data.update(
                        success=True, message="Sua petição foi enviada."
                    )
            else:
                response_data.update(errors=err2dict(form))
        else:
            response_data.update(message="Usuário ou token inválido.")
        self.render(response_data)

    @login_required(type="JSON")
    def __create_ged(self, upfile):
        buf = upfile.read()
        hashfilename = hashlib.md5(buf).hexdigest()

        ged = File.objects.filter(file=hashfilename)
        if not ged.exists():
            ged = File(
                filename=upfile.name,
                mimetype=upfile.content_type,
                file=hashfilename,
                user=self.request.user,
                acesso=3,
            )
            ged.save()
        else:
            ged = ged.first()

        self.__save_file(hashfilename, buf)

        return ged

    def __save_file(self, hashfilename, buf):
        filedir = File.directory_of_hash(hashfilename)
        filepath = os.path.join(filedir, hashfilename)

        if not os.path.exists(filedir):
            os.makedirs(filedir)

        if not os.path.exists(filepath):
            with open(filepath, "wb+") as f:
                f.write(buf)
