# -*- coding:utf-8 -*-

import hashlib

# from django.conf import settings
# from threading import Thread

from django.db.models import Q
from django.db import transaction
from django.core.mail import send_mail

from contrib.decorator import login_required
from contrib.utils import getLogger
from contrib.helpers import err2dict, clean_text
from contrib.controller import DefaultController
from rh.models import (
    Localidade,
    Endereco,
    Telefone,
    PessoaFisica,
    Lawyer,
    SeriousDiseases,
    SocialProgram,
)  # , PessoaJuridica

# from rh.parametros import NecessidadeEspecial
from rh.const import (
    TIPO_LOGRADOURO_ENDERECO_CHOICES,
    TIPO_ENDERECO_CHOICES,
    TIPO_TELEFONE_CHOICES,
    ESTADO_CIVIL_CHOICES,
    SEXO_CHOICES,
    GRAU_INSTRUCAO_CHOICES,
    RACA_COR_CHOICES,
)
from web.models import RegularWebUser, PasswordChangeRequest, TokenWebUser
from web.rpc.forms import (
    CreateIndividualUserForm,
    CreateLawyerUserForm,
    ChangePasswordForm,
    AuthenticateForm,
    TokenAuthenticateForm,
    UpdateIndividualUserForm,
    UpdateLawyerUserForm,
)


log = getLogger(__file__)


# Fallback do modulo transaction entre o django 1.8 e versões anteriores
if not hasattr(transaction, "atomic"):
    transaction.atomic = transaction.commit_on_success

"""
renda_familiar
social_program
has_serious_diseases
serious_diseases
"""

"""
nacionalidade
genero
profissao
has_serious_diseases
serious_diseases
renda_domiciliar -> renda_familiar
membro_familia_programa_social -> X
qual_programa_social -> social_program
"""


class MessageException(Exception):
    pass


class AccountManager(DefaultController):

    def __init__(self, *args, **kwargs):
        super(AccountManager, self).__init__(*args, **kwargs)
        self.set_restful("json")
        self.response["content-type"] = "text/javascript; charset=utf-8"

    def __to_options(self, choices):
        return [{"value": val, "text": text} for val, text in choices]

    @login_required(type="JSON")
    def form_options(self, args=[]):
        qs_cities = Localidade.objects.filter(estado__sigla="TO").order_by("nome")
        qs_disease = SeriousDiseases.objects.order_by("name")
        qs_social_program = SocialProgram.objects.order_by("name")
        data = {
            "cities": [{"value": city.id, "text": city.nome} for city in qs_cities],
            "education_kinds": self.__to_options(
                [[k, v] for k, v in list(GRAU_INSTRUCAO_CHOICES.items()) if k != 14]
            ),
            "disease_kinds": [
                {"value": disease.id, "text": disease.name} for disease in qs_disease
            ],
            "social_program_kinds": [
                {"value": social_program.id, "text": social_program.name}
                for social_program in qs_social_program
            ],
            "address_kinds": self.__to_options(TIPO_ENDERECO_CHOICES),
            "address_location_kinds": self.__to_options(
                TIPO_LOGRADOURO_ENDERECO_CHOICES
            ),
            "phone_kinds": self.__to_options(TIPO_TELEFONE_CHOICES),
            "marital_status_kinds": self.__to_options(ESTADO_CIVIL_CHOICES),
            "gender_kinds": self.__to_options(SEXO_CHOICES),
            "race_kinds": self.__to_options(RACA_COR_CHOICES),
        }
        self.render(data)

    @login_required(type="JSON")
    def authenticate(self, args=[]):
        response_data = {"success": False}
        form = AuthenticateForm(self.request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            user = RegularWebUser.authenticate(
                form_data["username"], form_data["password"]
            )
            if user:
                individual = getattr(user.person, "pessoafisica", None)
                is_lawyer = individual and hasattr(individual, "lawyer")
                check_data = "%s%s" % (user.username, user.email)
                response_data.update(
                    success=True,
                    message="Usuário autenticado.",
                    user={
                        "id": hashlib.md5(user.username.encode()).hexdigest(),
                        "username": user.username,
                        "name": user.person.nome,
                        "email": user.email,
                        "is_lawyer": is_lawyer,
                        "key_check": hashlib.md5(check_data.encode()).hexdigest(),
                    },
                )
            else:
                response_data.update(message="Usuário ou senha inválidos.")
        else:
            response_data.update(message="Preencha corretamente o formulário.")
        self.render(response_data)

    @login_required(type="JSON")
    def authenticate_token(self, args=[]):
        response_data = {"success": False}
        form = TokenAuthenticateForm(self.request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            user = TokenWebUser.objects.filter(token=form_data["token"]).first()
            if user:
                oid = hashlib.md5((user.token).encode()).hexdigest()
                check_data = "%s%s" % (oid, user.person.nome)
                response_data.update(
                    success=True,
                    message="Usuário autenticado.",
                    user={
                        "id": oid,
                        "username": "token-user",
                        "name": user.person.nome,
                        "key_check": hashlib.md5(check_data.encode()).hexdigest(),
                    },
                )
            else:
                response_data.update(message="Token inválido.")
        else:
            response_data.update(message="Preencha corretamente o formulário.")
        self.render(response_data)

    @login_required(type="JSON")
    def password_change_request(self, args=[]):
        response_data = {"success": False}

        email = self.request.POST.get("email")
        if email:
            user = RegularWebUser.objects.filter(email=email).first()
            if user:
                try:
                    change_request = PasswordChangeRequest(user=user)

                    with transaction.atomic():
                        change_request.save()

                        if self.request.POST.get("reset"):
                            email_params = {
                                "subject": "Requisição de alteração de senha",
                                "message": """
                                Foi realizada uma Solicitação de alteração de senha para o usuário associado a este email.

                                Para alterar sua senha copie o código abaixo e insira-o no campo "código de verificação".

                                %s

                                Ministério Público do Estado do Tocantins - Departamento de Tecnologia da Informação

                                """
                                % change_request.key,
                                "from_email": "system@mpto.mp.br",
                                "recipient_list": [email],
                            }

                            try:
                                send_mail(**email_params)
                            except Exception as ee:
                                log.error(ee)

                except Exception as e:
                    self.log.error(e)
                    response_data.update(
                        message="Não foi possível realizar operação. Erro: %s" % e
                    )
                else:
                    response_data.update(
                        success=True,
                        key=change_request.key,
                        message="Uma mensagem com o código para alteração de senha será enviada para email cadastrado.",
                    )
            else:
                response_data.update(
                    message="Solicitação de alteração de senha ignorada. Não existe usuário associado ao email: %s "
                    % email
                )
        else:
            response_data.update(message="Email não informado")

        self.render(response_data)

    @login_required(type="JSON")
    def password_change(self, args=[]):
        data = {"success": False, "message": "Dados inválidos"}
        form = ChangePasswordForm(self.request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            user = RegularWebUser.objects.filter(email=form_data["email"]).first()

            if user:
                passwd_request = user.password_change_requests.filter(
                    valid=True, key=form_data["key"]
                ).last()

                if passwd_request:
                    if form_data["password"] != form_data["confirmation"]:
                        data.update(message="Senhas não conferem.")
                    else:
                        try:
                            with transaction.atomic():
                                user.set_password(form_data["password"])
                                user.save()
                                passwd_request.valid = False
                                passwd_request.save()
                        except Exception as e:
                            self.log.error(e)
                            data.update(message="Erro: %s" % e)
                        else:
                            data.update(success=True, message="Senha alterada.")
                else:
                    data.update(message="Requisição de alteração de senha inválida.")
            else:
                data.update(message="Não existe usuário associado ao email informado.")
        else:
            data.update(errors=dict(form.errors))
        self.render(data)

    @login_required(type="JSON")
    def user_data(self, args=[]):
        data = {"success": False}
        user = RegularWebUser.objects.filter(
            username=self.request.POST.get("username")
        ).first()
        if user:
            _user_data = {
                "id": user.id,
                "user_kind": user.user_kind(),
                "username": user.username,
                "email": user.email,
                "name": user.person.nome,
            }

            address = user.person.address.first()
            if address:
                _user_data.update(
                    {
                        "address_kind": address.tipo_endereco,
                        "address_location_kind": address.tipo_logradouro,
                        "address": address.logradouro,
                        "city": getattr(address.municipio, "pk", "Não informado"),
                        "zipcode": address.cep,
                        "number": address.numero,
                        "neighborhood": address.bairro,
                        "extra": address.complemento,
                    }
                )

            phones = user.person.phone.all()
            if phones.exists():
                phone1 = phones.first()
                _user_data.update(
                    {"phone_kind": phone1.tipo_telefone, "phone": phone1.numero}
                )

                if phones.count() > 1:
                    phone2 = phones[1]
                    _user_data.update(
                        {"phone_kind2": phone2.tipo_telefone, "phone2": phone2.numero}
                    )

            if user.is_lawyer_user():
                _user_data.update(oab=user.person.pessoafisica.lawyer.oab)
            else:
                _user_data.update(
                    {
                        "cpf": user.person.pessoafisica.cpf,
                        "rg": user.person.pessoafisica.rg,
                        "gender": user.person.pessoafisica.sexo,
                        "genre": user.person.pessoafisica.genero,
                        "marital_status": user.person.pessoafisica.estado_civil,
                        "race": user.person.pessoafisica.raca_cor,
                        "birth_date": user.person.pessoafisica.data_nascimento,
                        "mother_name": user.person.pessoafisica.nome_mae,
                        "disease": [
                            disease.pk
                            for disease in user.person.pessoafisica.serious_diseases.all()
                        ],
                        "education": user.person.pessoafisica.grau_instrucao,
                        "nationality": user.person.pessoafisica.nacionalidade,
                        "profession": user.person.pessoafisica.profissao,
                        "income": user.person.pessoafisica.renda_familiar,
                        "social_program": [
                            s.pk for s in user.person.pessoafisica.social_program.all()
                        ],
                    }
                )

            data.update(success=True, user_data=_user_data)
        self.render(data)

    @login_required(type="JSON")
    def create_token_user(self, args=[]):
        data = {"success": False}
        try:
            user = TokenWebUser()
            with transaction.atomic():
                user.save()

        except Exception as e:
            log.info(e)
            data.update(message="Não foi possível criar usuário. %s" % e)
        else:
            data = {"success": True, "message": "Usuário criado", "token": user.token}

        self.render(data)

    @login_required(type="JSON")
    def delete_user(self, args=[]):
        response_data = {"success": False}
        pk = self.request.POST.get("id")
        if pk:
            user = RegularWebUser.objects.filter(pk=pk).first()
            if user:
                try:
                    with transaction.atomic():
                        user.delete()
                except Exception as e:
                    self.log.error(e)
                    response_data.update(message="Não foi possível deletar usuário.")
                else:
                    response_data.update(success=True, message="Usuário deletado.")
            else:
                response_data.update(message="Usuário não encontrado.")
        else:
            response_data.update(message="Informe o identificador do usuário")
        self.render(response_data)

    @login_required(type="JSON")
    def create_user(self, args=[]):
        forms = {"individual": CreateIndividualUserForm, "lawyer": CreateLawyerUserForm}

        self.render(self.__process_save(forms))

    @login_required(type="JSON")
    def update_user(self, args=[]):
        forms = {"individual": UpdateIndividualUserForm, "lawyer": UpdateLawyerUserForm}

        self.render(self.__process_save(forms))

    @login_required(type="JSON")
    def __process_save(self, forms={}):
        data = {"success": False, "message": ""}

        user_kind = self.request.POST.get("user_kind") or "individual"

        request_data = self.request.POST.dict()

        if user_kind == "individual":
            try:
                request_data["disease"] = eval(self.request.POST.get("disease"))
                request_data["social_program"] = eval(
                    self.request.POST.get("social_program")
                )
            except:
                request_data["disease"] = self.request.POST.getlist("disease")
                request_data["social_program"] = self.request.POST.getlist(
                    "social_program"
                )

        Form = forms.get(user_kind)

        form = Form(request_data)

        if form.is_valid():
            form_data = form.cleaned_data
            check = (
                lambda q: RegularWebUser.objects.exclude(pk=form_data.get("id"))
                .filter(q)
                .exists()
            )

            if check(Q(username=form_data["username"])):
                data.update(message="Usuário já existe.")
            elif check(Q(email=form_data["email"])):
                data.update(message="Email já está sendo utilizado")
            else:
                try:
                    with transaction.atomic():
                        self.__save_user(form_data)
                except MessageException as msg:
                    data.update(message="Não foi possível salvar usuário. %s" % msg)
                except Exception as e:
                    log.error(e)
                    log.info(e)
                    data.update(
                        message="Não foi possível salvar usuário.", err="%s" % e
                    )
                else:
                    data = {"success": True, "message": "Usuário salvo."}
        else:
            data.update(
                message="Preencha corretamente o formulário.", errors=err2dict(form)
            )

        return data

    @login_required(type="JSON")
    def __save_user(self, form_data):
        pk = form_data.get("id")
        user = RegularWebUser.objects.get(pk=pk) if pk else RegularWebUser()

        if hasattr(user, "person"):
            form_data["person_instance"] = user.person

        person = self.__save_person(form_data)
        # log.info(person)
        # log.info(getattr(person, 'pk', 'Sem pk'))

        if (
            not pk
            and hasattr(person, "pessoa_ptr")
            and RegularWebUser.objects.filter(person=person.pessoa_ptr).exists()
        ):
            raise MessageException("Essa pessoa já está associada a um usuário.")

        user.username = form_data["username"]
        user.email = form_data["email"]
        user.person = person.pessoa_ptr

        if not pk:
            user.set_password(form_data["password"])

        user.save()

    @login_required(type="JSON")
    def __save_person(self, form_data):

        # base_person = form_data.get('person_instance') or {}
        user_kind = form_data.get("user_kind")
        person = form_data.get("person_instance") or {}
        individual = person.pessoafisica if hasattr(person, "pessoafisica") else None
        is_employee = False

        if user_kind == "individual":
            cpf = {}
            if form_data.get("cpf"):
                cpf = {"cpf": clean_text(form_data["cpf"])}

            filter_params = cpf or {
                "nome__iexact": form_data["name"],
                "nome_mae__iexact": form_data["mother_name"],
            }

            person = (
                individual
                or PessoaFisica.objects.filter(**filter_params).first()
                or PessoaFisica()
            )

            is_employee = person.servidor_set.all().exists()

            person._skip_signal = True
            person.email_institucional = form_data["email"]
            person.nome_mae = form_data["mother_name"]
            person.cpf = clean_text(form_data["cpf"])
            person.rg = clean_text(form_data["rg"])
            person.sexo = form_data["gender"] or None
            person.estado_civil = form_data["marital_status"] or 7
            person.raca_cor = form_data["race"] or 5
            person.data_nascimento = form_data["birth_date"]
            if form_data["education"]:
                person.grau_instrucao = form_data["education"]
            person.nacionalidade = form_data["nationality"]
            person.genero = form_data["genre"]
            person.profissao = form_data["profession"]
            person.renda_familiar = form_data["income"] or 0.0

        elif user_kind == "lawyer":
            oab_number = clean_text(form_data["oab"])
            person = (
                individual
                or Lawyer.objects.filter(oab=oab_number).first()
                or Lawyer(oab=oab_number)
            )

        # elif form_data.get('cnpj'):
        #     person = PessoaJuridica.objects.filter(cnpj=form_data['cnpj']).first()
        #     if not person:
        #         person = PessoaJuridica(
        #             cnpj=form_data['cnpj'],
        #             razao_social=form_data['name']
        #         )

        else:
            raise MessageException("Tipo de pessoa inválido.")

        if not is_employee:

            person.nome = form_data["name"]
            person.save_sem_cpf()

            if form_data.get("disease"):
                person.serious_diseases.clear()
                person.has_serious_diseases = True
                diseases = list(form_data["disease"])
                person.serious_diseases.add(*diseases)
            else:
                person.has_serious_diseases = False

            if form_data.get("social_program"):
                person.social_program.clear()
                social_program = list(form_data["social_program"])
                person.social_program.add(*social_program)

            if form_data.get("address"):
                person_address = person.address.all()

                address = person_address.first() or Endereco()
                address.tipo_endereco = form_data["address_kind"] or 1
                address.tipo_logradouro = form_data["address_location_kind"] or 7
                address.cep = clean_text(form_data["zipcode"])
                address.logradouro = form_data["address"]
                address.numero = form_data["number"]
                address.bairro = form_data["neighborhood"]
                address.complemento = form_data["extra"]
                address.municipio = form_data["city"]
                address.person = person

                address.save()

            phones = []
            if form_data.get("phone"):
                phones.append(
                    {"kind": form_data["phone_kind"] or 1, "number": form_data["phone"]}
                )
            if form_data.get("phone2"):
                phones.append(
                    {
                        "kind": form_data["phone_kind2"] or 1,
                        "number": form_data["phone2"],
                    }
                )

            for p in phones:
                person_phone = person.phone.filter(numero=p["number"])

                phone = person_phone.first() or Telefone()
                phone.tipo_telefone = p["kind"]
                phone.numero = clean_text(p["number"])
                phone.person = person
                phone.save()

        return person

    # @login_required(type='JSON')
    # def get_person(self, form_data):
    #     person = None
    #     if form_data.get('cpf'):
    #         person = PessoaFisica.objects.filter(cpf=form_data['cpf']).first()
    #         if not person:
    #             person = PessoaFisica(cpf=form_data['cpf'])
    #     elif form_data.get('cnpj'):
    #         person = PessoaJuridica.objects.filter(cnpj=form_data['cnpj']).first()
    #         if not person:
    #             person = PessoaJuridica(
    #                 cnpj=form_data['cnpj'],
    #                 razao_social=form_data['name']
    #             )
    #     else:
    #         raise Exception('É necessário informar o CPF ou CNPJ.')

    #     if hasattr(person, 'pessoa_ptr') and RegularWebUser.objects.filter(person=person.pessoa_ptr).exists():
    #         raise Exception('Essa pessoa já está associada a um usuário.')

    #     return person
