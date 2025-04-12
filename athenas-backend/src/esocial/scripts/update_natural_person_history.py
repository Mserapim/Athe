# -.- coding: utf-8 -.-
import getopt
import sys
import django
import os
from pprint import pprint

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()


from esocial.models import S2205
from esocial.const import RACE_MAP, MARITAL_STATUS_MAP
from rh.models import (
    Localidade,
    PessoaFisica,
    Pais,
    TYPE_PHONE_EMERGENCY,
    NaturalPersonHistory,
    Pais,
)
from contrib.utils import DateUtils
from contrib.middleware import set_current_user


set_current_user("athenas")

VERBOSE = True
USAGE = f"Usage: {sys.argv[0]} " "[--verbose <True/False>] ]"


def update_natural_person_history(event):
    np_history = NaturalPersonHistory.objects.filter(
        natural_person__cpf=event.ide_trabalhador_cpf_trab,
        when=event.alteracao_dt_alteracao,
    ).last()
    if not np_history:
        np_history, created = NaturalPersonHistory.objects.get_or_create(
            when=event.alteracao_dt_alteracao,
            natural_person=PessoaFisica.objects.filter(
                cpf=event.ide_trabalhador_cpf_trab
            ).first(),
        )
        if VERBOSE:
            print(f"{event.description} não possui NaturalPersonHistory!\nSerá criado!")
            print(f"created: {created} - {np_history}")

    person = np_history.natural_person

    def natural_person(event):
        return PessoaFisica.objects.filter(cpf=event.ide_trabalhador_cpf_trab).last()

    def address(person, exclude_outsider=True):
        return person.address.exclude(outsider=exclude_outsider).last()

    def _tipo_logradouro(value):
        _map = {
            "AV": 1,
            "PC": 2,
            "Q": 9,
            "R": 8,
            "VD": 5,
            "VLA": 3,
            "IND": 6,
            "IND": 6,
            "IND": 6,
            "TV": 10,
            "O": 11,
        }
        return _map.get(value, 1)

    def _localidade(value):
        try:
            return Localidade.objects.filter(ibge=value).first()
        except Exception as err:
            print(err)
            print(f"IBGE: {value} - {Localidade.objects.filter(ibge=value)}")

    def _tipo_endereco(person, exclude_outsider=True):
        add = address(person, exclude_outsider=exclude_outsider)
        return add.tipo_endereco if add else None

    tipo_endereco = _tipo_endereco(person)
    country = None
    outsider_citty = None
    outsider = False
    if event.exterior_pais_resid:
        outsider = True
        country = Pais.objects.get(esocial_code=event.exterior_pais_resid)
        outsider_citty = event.exterior_nm_cid
        tipo_endereco = _tipo_endereco(person, exclude_outsider=False)

    def _phone(person, number, main=True, type_phone=None):
        query = person.phone.filter(numero=number)
        if main:
            query = query.filter(main=main)
        if type_phone:
            query = query.filter(tipo_telefone=type_phone)
        return query.last()

    def _phone_type(person, number):
        phone = _phone(person, number)
        if phone:
            return phone.tipo_telefone
        return None

    def _phone_public(person, number):
        phone = _phone(person, number)
        if phone:
            return phone.publico
        return None

    def _phone_description(person, number):
        phone = _phone(person, number)
        if phone:
            return phone.description
        return None

    def _phone_contact_emergency(person, number):
        phone = _phone(person, number, main=False, type_phone=TYPE_PHONE_EMERGENCY)
        if phone:
            return phone.numero
        return None

    def _contact_emergency_name(person, number):
        phone = _phone(person, number, main=False, type_phone=TYPE_PHONE_EMERGENCY)
        if phone:
            return phone.description
        return None

    np_history.tipo_logradouro = _tipo_logradouro(event.brasil_tp_lograd)
    np_history.tipo_endereco = tipo_endereco
    np_history.municipio = _localidade(event.brasil_cod_munic)
    np_history.logradouro = event.brasil_dsc_lograd
    np_history.bairro = event.brasil_bairro
    np_history.cep = event.brasil_cep
    np_history.numero = event.brasil_nr_lograd
    np_history.complemento = event.brasil_complemento
    np_history.outsider = outsider
    np_history.country = country
    np_history.outsider_citty = outsider_citty

    np_history.phone_main = event.contato_fone_princ
    np_history.phone_type = _phone_type(person, event.contato_fone_princ)
    np_history.phone_public = _phone_public(person, event.contato_fone_princ)
    np_history.phone_description = _phone_description(person, event.contato_fone_princ)
    np_history.phone_contact_emergency = _phone_contact_emergency(
        person, event.contato_fone_princ
    )
    np_history.contact_emergency_name = _contact_emergency_name(
        person, event.contato_fone_princ
    )

    cnh_numero = None
    cnh_categoria = None
    cnh_expedition_date = None
    cnh_first_date = None
    cnh_state = None
    cnh_validity_date = None
    cnh = person.cnh
    if cnh:
        cnh_numero = cnh.numero
        cnh_categoria = cnh.cnh_category.valor
        cnh_expedition_date = cnh.data_expedicao
        cnh_first_date = (
            DateUtils.str_to_date(cnh.cnh_first_date.valor)
            if cnh.cnh_first_date
            else None
        )
        cnh_state = cnh.estado_expedicao
        cnh_validity_date = cnh.data_validade

    np_history.cnh = cnh_numero
    np_history.cnh_categoria = cnh_categoria
    np_history.cnh_expedition_date = cnh_expedition_date
    np_history.cnh_first_date = cnh_first_date
    np_history.cnh_state = cnh_state
    np_history.cnh_validity_date = cnh_validity_date

    professional_council = person.professional_council
    professional_council_number = None
    professional_council_state = None
    professional_council_expedition_date = None
    professional_council_validity_date = None
    professional_council_issuer = None

    if professional_council:
        professional_council_number = professional_council.numero
        professional_council_state = professional_council.estado_expedicao
        professional_council_expedition_date = professional_council.data_expedicao
        professional_council_validity_date = professional_council.data_validade
        professional_council_issuer = (
            professional_council.professional_council_issuer.valor
        )

    np_history.professional_council = professional_council_number
    np_history.professional_council_state = professional_council_state
    np_history.professional_council_expedition_date = (
        professional_council_expedition_date
    )
    np_history.professional_council_validity_date = professional_council_validity_date
    np_history.professional_council_issuer = professional_council_issuer

    nis = person.pis_pasep
    np_history.nis = nis.numero if nis else None

    reservist = person.reservist
    reservista_numero = None
    classe_reservista = None
    if reservist:
        reservista_numero = reservist.numero
        classe_reservista = (
            reservist.reservist_class.valor if reservist.reservist_class else None
        )

    np_history.reservista = reservista_numero
    np_history.classe_reservista = classe_reservista

    voter = person.voter
    titulo_eleitor = None
    municipio_titulo = None
    secao_titulo = None
    zona_titulo = None
    if voter:
        titulo_eleitor = voter.numero
        voter_city = voter.voter_city
        if voter_city:
            municipio_titulo = Localidade.objects.filter(ibge=voter_city.valor).last()
        secao_titulo = voter.voter_section.valor
        zona_titulo = voter.voter_zone.valor
    np_history.titulo_eleitor = titulo_eleitor
    np_history.municipio_titulo = municipio_titulo
    np_history.secao_titulo = secao_titulo
    np_history.zona_titulo = zona_titulo

    ctps = person.ctps
    ctps_state = None
    serie_ctps = None
    if ctps:
        ctps_state = ctps.estado_expedicao
        serie_ctps = ctps.ctps_series.valor
        ctps = ctps.numero

    np_history.ctps = ctps
    np_history.ctps_state = ctps_state
    np_history.serie_ctps = serie_ctps

    np_history.pis_pasep = np_history.nis

    np_history.cpf = event.ide_trabalhador_cpf_trab

    np_history.data_nascimento = person.data_nascimento
    np_history.data_obito = person.data_obito
    np_history.doador = person.doador

    uniao_estavel = person.uniao_estavel
    np_history.uniao_estavel = True if uniao_estavel else None
    np_history.email_pessoal = person.email_pessoal
    marital_map = {v: k for k, v in MARITAL_STATUS_MAP.items()}
    np_history.estado_civil = marital_map.get(event.dados_trabalhador_est_civ)
    np_history.fator_rh = person.fator_rh
    np_history.foto = person.foto

    def _grau_instrucao(value):
        _map = {
            "01": 1,
            "02": 15,
            "03": 16,
            "04": 17,
            "05": 4,
            "06": 5,
            "07": 6,
            "08": 7,
            "09": 8,
            "10": 9,
            "11": 10,
            "12": 11,
        }
        return _map.get(value, 1)

    np_history.grau_instrucao = _grau_instrucao(event.dados_trabalhador_grau_instr)
    np_history.municipio_naturalidade = person.municipio_naturalidade
    np_history.nationality = person.nationality

    np_history.nationality_birth = Pais.objects.get(
        esocial_code=event.dados_trabalhador_pais_nac
    )
    np_history.immigrant_residence_time = event.trab_imig_tmp_resid
    np_history.immigrant_entry_condition = event.trab_imig_cond_ing

    np_history.nome = event.dados_trabalhador_nm_trab
    np_history.nome_conjuge = person.nome_conjuge
    np_history.nome_mae = person.nome_mae
    np_history.phonetic_father_name = person.phonetic_father_name
    np_history.nome_pai = person.nome_pai
    np_history.phonetic_mother_name = person.phonetic_mother_name
    np_history.genero = person.genero
    race_map = {v: k for k, v in RACE_MAP.items()}
    np_history.raca_cor = race_map.get(event.dados_trabalhador_raca_cor)

    np_history.rg = person.rg
    np_history.rg_data_expedicao = person.rg_data_expedicao
    np_history.rg_orgao = person.rg_orgao
    np_history.rg_uf = person.rg_uf

    np_history.sangue = person.sangue
    np_history.sexo = event.dados_trabalhador_sexo
    np_history.sexual_orientation = person.sexual_orientation

    np_history.social_name = event.dados_trabalhador_nm_soc

    np_history.necessidade_especial = person.necessidade_especial

    np_history.profissao = person.profissao
    np_history.renda_familiar = person.renda_familiar
    np_history.has_serious_diseases = person.has_serious_diseases
    np_history.retired = person.retired
    np_history.is_lawyer = person.is_lawyer
    np_history.oab = person.oab

    np_history.name_cache = person.name_cache
    np_history.phonetic_name = person.phonetic_name
    np_history.slug = person.slug
    np_history.email = person.email
    np_history.enable_protocol = person.enable_protocol
    np_history.kind = person.kind
    np_history.rate_fill = person.rate_fill

    np_history.send_esocial = True
    np_history.save()
    return np_history.diff


def run_create_update_history_from_s2205():
    for event in S2205.objects.valids_by_status().order_by(
        "dados_trabalhador_nm_trab", "alteracao_dt_alteracao"
    ):
        event = event.event
        _diff = update_natural_person_history(event)
        if _diff and VERBOSE:
            print(event)
            pprint(_diff)


def run_create_history_dependence():
    NaturalPersonHistory.cmd_create_history_dependence()


def parse():
    options, arguments = getopt.getopt(
        sys.argv[1:],
        "vhs:",
        ["verbose"],
    )
    for o, a in options:
        if o in ("-v", "--verbose"):
            try:
                if len(arguments) and arguments[0].lower() == "false":
                    global VERBOSE
                    VERBOSE = False
                else:
                    raise SystemExit(
                        "Informe um valor válido para versbose(True/False). Ex: -v True. Default é True."
                    )
            except ValueError:
                raise SystemExit(USAGE)


def main() -> None:
    parse()
    rs_s2205 = input(
        "Criar e atualizar NaturalPersonHistory a partir do S2205? (s/N): "
    )
    rs_dependence = input(
        "Criar  NaturalPersonHistory a partir de Dependencia de Dependentes? (s/N): "
    )

    if rs_s2205.lower() == "s":
        run_create_update_history_from_s2205()
    if rs_dependence.lower() == "s":
        run_create_history_dependence()


if __name__ == "__main__":
    main()
