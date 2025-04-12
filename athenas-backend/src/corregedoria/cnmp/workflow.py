# -*- coding: utf-8 -*-
import re

from datetime import time, datetime
from django.conf import settings
from django.db.models import Max
from contrib.utils import DateUtils, employee_from_user, getLogger
from django.template.defaultfilters import slugify
from corregedoria.cirdir.models import Address, Teaching
from rh.models import MovimentacaoPosse, Servidor
from rh.scmmp.models import ProcessoJudicial

from corregedoria.cnmp.webservice import WSClient

log = getLogger(__name__)


class ExportDataEmployee(object):

    @classmethod
    def load_teaching(cls, controlinformation, wsclient):
        # verificar reaproveitamento de chamada ao webservice para obter os dados.

        magisterios = []

        disciplinas_ws = wsclient.get_disciplinas()
        estados = wsclient.get_estados()
        exerce_magisterio = False

        if controlinformation:
            mag_obj = wsclient.get_type("ns0:exercicioMagisterio")
            factory = wsclient.get_factory()

            meio_dia = time(12, 0)
            noite = time(18, 0)

            # verifica se dar aula em algum dos periodos
            for teaching in controlinformation.in_teaching.filter(
                discipline__isnull=False
            ):
                turno_matutuino = False
                turno_vespertino = False
                turno_noturno = False
                exerce_magisterio = True
                for schedule in teaching.schedule.all():
                    time_initial = datetime.strptime(
                        schedule.start_time, "%H:%M:%S"
                    ).time()
                    if time_initial < meio_dia:
                        turno_matutuino = True
                    elif time_initial > meio_dia and time_initial < noite:
                        turno_vespertino = True
                    elif time_initial > noite:
                        turno_noturno = True

                disciplinas_ministradas = []

                for dw in disciplinas_ws:
                    if Teaching.objects.filter(
                        id=teaching.id, discipline__name__icontains=dw.nome
                    ).exists():
                        disciplinas_ministradas.append(dw)

                municipio_magisterio = ""
                for estado in estados:
                    if estado.sigla == teaching.institution.county.estado.sigla:
                        municipios = wsclient.get_municipios_por_estado(estado.id)
                        for munic in municipios:
                            if slugify(munic.nome) == slugify(
                                teaching.institution.county.nome
                            ):
                                municipio_magisterio = munic

                magisterios.append(
                    factory.exercicioMagisterio(
                        nomeInstituicao=teaching.institution.nome,
                        tipoCargo="PROFESSOR",
                        cargaHoraria=teaching.work_hours,
                        dataInicio=teaching.start_date.strftime("%Y-%m-%d"),
                        dataFim=teaching.end_date.strftime("%Y-%m-%d"),
                        municipio=municipio_magisterio,
                        turnoMatutino=turno_matutuino,
                        turnoVespertino=turno_vespertino,
                        turnoNoturno=turno_noturno,
                        listaDisciplinasMinistradas=disciplinas_ministradas,
                    )
                )

        return magisterios, exerce_magisterio

    @classmethod
    def load_postgraduate(
        cls, employee=None, course_area=None, type_course=None, wsclient=None
    ):
        pos_graduacoes = []

        ps_g = wsclient.get_type("ns0:posGraduacao")

        if wsclient:
            course_area = wsclient.get_areas_cursos()
            type_course = wsclient.get_tipos_pos_graduacao()

        for ig in employee.improvement_and_graduate.all():
            area_curso_pos = None
            for ac_pos in course_area:
                if ac_pos.id == ig.course_area.value:
                    area_curso_pos = ac_pos

            tipo_pos = None
            for tp in type_course:
                if tp.id == ig.nivel:
                    tipo_pos = tp

            pos_graduacoes.append(
                ps_g(
                    nomeCurso=re.sub(r"[“|”]", r"", ig.course[:59]),
                    tipo=tipo_pos,
                    nomeInstituicao=ig.institution,
                    areaCurso=area_curso_pos,
                    anoConclusao=ig.conclusion_year,
                )
            )

        return pos_graduacoes

    @classmethod
    def load_graduate(cls, employee=None, course_area=None, wsclient=None):
        graduacoes = []
        gr_ws = wsclient.get_type("ns0:graduacao")

        if wsclient:
            course_area = wsclient.get_areas_cursos()

        for g in employee.graduation.all():
            area_curso_grad = None
            for ac in course_area:
                if ac.id == g.course_area.value:
                    area_curso_grad = ac

            graduacoes.append(
                gr_ws(
                    nomeCurso=g.course[:59],
                    nomeInstituicao=g.institution,
                    areaCurso=area_curso_grad,
                    anoConclusao=g.conclusion_year,
                )
            )

        return graduacoes

    @classmethod
    def load_published_article(
        cls, employee=None, type_publication=None, wsclient=None
    ):
        trabalhos_publicados = []
        pub_ws = wsclient.get_type("ns0:trabalhoPublicado")

        if wsclient:
            type_publication = wsclient.get_obtem_tipos_trabalhos_publicados()

        for trab in employee.published_works.all():

            tipos_trab = None
            for t_trab in type_publication:
                if t_trab.id == trab.work_type:
                    tipos_trab = t_trab

            trabalhos_publicados.append(
                pub_ws(
                    titulo=re.sub(r"[“|”]", r"", trab.title),
                    anoPublicacao=trab.year,
                    area=trab.area,
                    tipoTrabalhoPublicado=tipos_trab,
                    meioPublicacao=trab.publication_place,
                    nomeInstituicao=trab.institution,
                )
            )

        return trabalhos_publicados

    @classmethod
    def load_hometown(cls, employee=None, wsclient=None):
        municipio = ""

        states = wsclient.get_estados()

        for estado in states:
            if (
                estado.sigla
                == employee.pessoa_fisica.municipio_naturalidade.estado.sigla
            ):
                municipios = wsclient.get_municipios_por_estado(estado.id)
                for munic in municipios:
                    if slugify(munic.nome) == slugify(
                        employee.pessoa_fisica.municipio_naturalidade.nome
                    ):
                        municipio = munic
                        break

        return municipio

    @classmethod
    def load_current_worker_location(cls, employee=None, branch=None, wsclient=None):
        lotacao_atual = None
        lot = None

        organic_units = wsclient.get_unidades_organicas(branch)

        if employee.get_workplace().filter(ativo=True).exists():
            lot = slugify(employee.get_workplace().filter(ativo=True)[0].lotacao.sigla)
        elif employee.get_workplace_only().filter(ativo=True).exists():
            lot = slugify(
                employee.get_workplace_only()
                .filter(ativo=True)
                .order_by("-created_at")
                .first()
                .lotacao.sigla
            )
        elif employee.work_locations.filter(ativo=True, organograma=True).exists():
            lot = slugify(
                employee.work_locations.filter().filter(ativo=True)[0].lotacao.sigla
            )

        for unidade in organic_units:
            if lot and slugify(unidade.sigla) == lot:
                lotacao_atual = unidade

        return lotacao_atual

    @classmethod
    def load_type_inactivation(
        cls, employee=None, last_possession=None, inactivation_list=None, wsclient=None
    ):
        inativacao = None
        if not last_possession:
            last_possession = employee.posses.filter(
                quadro__cargo__tipo_lei_cargo="EF"
            ).last()

        if wsclient:
            inactivation_list = wsclient.get_motivos_inativacao()

        if not employee.ativo and last_possession.data_desligamento:

            for mot in inactivation_list:
                kind = slugify(
                    last_possession.desligamento.get_tipo_desligamento_display()
                ).split("-")[0]
                # no athenas esta cadastrado como falecimento. SCNMP como morte
                if kind == "falecimento":
                    kind = "morte"

                if slugify(mot.nome) == kind:
                    inativacao = mot
                    break

        if inativacao:
            factory = wsclient.get_factory()
            inativacao = factory.inativacao(
                motivoInativacao=inativacao,
                dataInicio=last_possession.data_desligamento,
            )
        return inativacao

    @classmethod
    def load_address(cls, controlinformation=None, wsclient=None):

        residencia = {}
        reside_localidade = "SIM"

        address = Address.objects.filter(controlinformation=controlinformation).first()

        if address:
            reside_localidade = "SIM" if address.validate_reside_outside else "NAO"

            # PEGAR O OBJETO RESIDENCIA FORA LOCALIDADE RETORNANDO O MUNICIPIO
            estados = wsclient.get_estados()
            municipio_residencia = ""
            for estado in estados:
                if estado.sigla == address.ref_address.municipio.estado.sigla:
                    municipios = wsclient.get_municipios_por_estado(estado.id)
                    for munic in municipios:
                        if slugify(munic.nome) == slugify(
                            address.ref_address.municipio.nome
                        ):
                            municipio_residencia = munic

            residencia["municipio"] = municipio_residencia
            residencia["atoAutorizacao"] = "NAO INFORMADO"

        return residencia, reside_localidade

    @classmethod
    def load_praise(cls, wsclient=None):
        elogios = []

        return elogios

    @classmethod
    def load_career_progression(cls, employee=None, wsclient=None):
        career = []
        factory = wsclient.get_factory()
        cargos = wsclient.get_cargos()

        # ISSO VAI DAR PROBLEMA SE MUDAR O NOME DOS CARGOS
        dict_cargos = {
            "1a-entrancia": slugify("Promotor(a) de Justiça de 1ª Entrância"),
            "2a-entrancia": slugify("Promotor(a) de Justiça de 2ª Entrância"),
            "3a-entrancia": slugify("Promotor(a) de Justiça de 3ª Entrância"),
            "procuradoria": slugify("Procurador(a) de Justiça"),
            "substituto": slugify("Promotor(a) de Justiça Substituto/Adjunto"),
        }

        for mov in employee.posses.filter(quadro__cargo__tipo_lei_cargo="EF"):
            slug = (
                slugify(mov.quadro.cargo.lotacao_responsavel.entrancia.nome)
                if mov.quadro.cargo.lotacao_responsavel
                else "substituto"
            )
            for cargo in cargos:
                if slugify(cargo.nome) == dict_cargos.get(slug, None):
                    career.append(
                        factory.progressaoCarreira(
                            cargo=cargo,
                            dataInicio=mov.data_exercicio,
                            dataFim=mov.data_desligamento,
                        )
                    )

        return career

    @classmethod
    def prepare_data_to_send(cls, pk=None, wsclient=None):

        if wsclient is None:
            wsclient = cls.factory_ws(type="production")

        ramos = wsclient.get_ramos()

        # aqui verifica o ramo pelo ID, talvez pegar pela sigla 'MP/TO'
        ramo_mpto = [r for r in ramos if r.id == 532][0]

        employee = Servidor.objects.get(pk=pk)
        print("Dados do Membro: {0}".format(employee))

        movimentacoes = MovimentacaoPosse.objects.filter(
            servidor=employee, quadro__cargo__tipo_lei_cargo="EF"
        ).order_by("data_exercicio")

        mov_primeira = movimentacoes.first()
        mov_ultima = movimentacoes.last()

        controlinformation = employee.controlinformations.filter(
            year=employee.controlinformations.aggregate(Max("year")).get("year__max"),
            employee=employee,
        ).first()

        residencia, reside_localidade = cls.load_address(
            controlinformation=controlinformation, wsclient=wsclient
        )

        # retorna o tipo de desligamento
        # motivos_inativacao = wsclient.get_motivos_inativacao()
        inativacao = cls.load_type_inactivation(employee=employee, wsclient=wsclient)

        # UNIDADES ORGANICAS - >>>> obs deve haver os cargos cadastrados no SCMMP
        lotacao_atual = cls.load_current_worker_location(
            employee=employee, branch=ramo_mpto, wsclient=wsclient
        )

        # RETORNANDO A CIDADE DE NASCIMENTO DO MEMBRO VIA WS DO CNMP
        municipio = cls.load_hometown(employee=employee, wsclient=wsclient)

        # Dados Graduacoes
        course_area = wsclient.get_areas_cursos()
        graduacoes = cls.load_graduate(employee=employee, wsclient=wsclient)

        # Dados Pos Graduacoes
        type_course = wsclient.get_tipos_pos_graduacao()
        pos_graduacoes = cls.load_postgraduate(
            employee=employee,
            course_area=course_area,
            type_course=type_course,
            wsclient=wsclient,
        )

        # Dados Trabalhos Publicados
        type_publication = wsclient.get_obtem_tipos_trabalhos_publicados()
        trabalhos_publicados = cls.load_published_article(
            employee=employee, type_publication=type_publication, wsclient=wsclient
        )

        # informacoes de magisterio
        magisterios, exerce_magisterio = cls.load_teaching(controlinformation, wsclient)

        # elogias
        elogio = cls.load_praise(wsclient)

        # carrega dados da carreira do membro
        carreira = cls.load_career_progression(employee=employee, wsclient=wsclient)

        pessoa_fisica = wsclient.get_factory().pessoaFisica(
            nome=employee.pessoa_fisica.nome,
            cpf=employee.pessoa_fisica.cpf,
            nomeMae=employee.pessoa_fisica.nome_mae,
            dataNascimento=employee.pessoa_fisica.data_nascimento.strftime("%Y-%m-%d"),
            ric=employee.pessoa_fisica.rg,
            sexo="MAS" if employee.pessoa_fisica.sexo == "M" else "FEM",
            estadoCivil=employee.pessoa_fisica.get_estado_civil_display()[0:3],
            exerceMagisterio=exerce_magisterio,
            emailInstitucional=getattr(employee.user, "email", "").replace(" ", ""),
            municipio=municipio,
            email=employee.pessoa_fisica.email_institucional,
        )

        def get_data_nomeacao():
            data_publicacao = None
            data_expedicao = None
            data_posse = mov_primeira.data_posse

            if mov_primeira.publicacao_movimentacao:
                data_publicacao = mov_primeira.publicacao_movimentacao.data_publicacao
                data_expedicao = mov_primeira.publicacao_movimentacao.data_expedicao
            else:
                return data_posse

            if data_publicacao and data_publicacao <= data_posse:
                return data_publicacao
            elif data_expedicao and data_expedicao <= data_posse:
                return data_expedicao
            else:
                return data_posse

        membro = wsclient.get_factory().membro(
            pessoaFisica=pessoa_fisica,
            matricula=employee.matricula,
            # foto=None,
            divulgacaoAutorizada=False,
            graduacoes=graduacoes,
            inativacao=inativacao,
            posGraduacoes=pos_graduacoes,
            trabalhosPublicados=trabalhos_publicados,
            nomeacao=get_data_nomeacao().strftime("%Y-%m-%d"),
            posse=mov_primeira.data_posse.strftime("%Y-%m-%d"),
            exercicio=mov_primeira.data_exercicio.strftime("%Y-%m-%d"),
            ultimaPromocao=mov_ultima.data_exercicio.strftime("%Y-%m-%d"),
            advocaciaExercida=False,  # NAO TEM ESSA INFORMACAO NO ATHENAS
            situacao=(
                "ATIVO"
                if employee.ativo and not mov_ultima.data_desligamento
                else "INATIVO"
            ),
            estrangeiro=False,  # NAO TEM ESSA INFORMACAO PREENCHIDA NO ATHENAS
            resideLocalidade=reside_localidade,
            residencia=residencia,
            lotacaoAtual=lotacao_atual,
            magisterios=magisterios,
            elogios=elogio,
            cidadeEstrangeiro=None,
            progressoesCarreira=carreira,
        )

        return membro

    @classmethod
    def factory_ws(cls, type="homologation"):
        wsclient = None

        if type == "production":
            wsclient = WSClient(
                url=getattr(settings, "WS_SCMMP_PRODUCAO_URL"),
                user=getattr(settings, "WS_SCMMP_PRODUCAO_USER"),
                passwd=getattr(settings, "WS_SCMMP_PRODUCAO_PASSWORD"),
            )
        else:
            wsclient = WSClient(
                url=getattr(settings, "WS_SCMMP_HOMOLOGA_URL"),
                user=getattr(settings, "WS_SCMMP_HOMOLOGA_USER"),
                passwd=getattr(settings, "WS_SCMMP_HOMOLOGA_PASSWORD"),
            )
        return wsclient

    @classmethod
    def run(cls, pk, production=False):

        type_ws = "production" if production else "homologation"
        report = cls.prepare_data_to_send(pk=pk)
        response = None
        try:
            wsclient = cls.factory_ws(type=type_ws)
            response = wsclient.send_data(report)
        except Exception as e:
            print(e)
            raise e
        finally:
            return response


class ExportDataProcess(object):

    def run(self):

        wsclient = WSClient(
            url="https://scmmp-homologacao.cnmp.mp.br/scmmp/services/ProcessoJudicialWS?wsdl",
            user=getattr(settings, "WS_SCMMP_HOMOLOGA_USER", None),
            passwd=getattr(settings, "WS_SCMMP_HOMOLOGA_PASSWORD", None),
        )

        ramos = wsclient.get_ramos()
        ramo_mpto = [r for r in ramos if r.id == 532][0]
        processos_judiciais = []
        for pj in ProcessoJudicial.objects.all():
            try:
                membrosProcessos = []
                faseRecursal = []
                processo_judicial = {
                    "ramo": ramo_mpto,
                    "numeroCNJ": pj.numero_cnj,
                    "numeroLocal": pj.numero_local,
                    "orgaoJulgador": pj.orgao_julgador,
                    "nomeAcao": pj.nome_acao,
                    "url": pj.url,
                    "tipoProcessoJudicial": pj.get_tipo_processo_judicial_display(),
                    "resumo": pj.resumo,
                    "observacao": pj.observacao,
                    "justificativaExclusao": pj.justificativa_exclusao,
                    "ativo": pj.ativo,
                    "situacaoPreenchimento": "PCO",
                }

                for mproc in pj.membro_processo.all():
                    sancoes = []
                    # DADOS DA SANCAO AO MEMBRO
                    for sj in mproc.sancaojudicial.all():
                        sancoes.append(
                            {
                                "resumo": sj.resumo,
                                "dataImposicao": (
                                    sj.data_imposicao.strftime("%Y-%m-%d")
                                    if sj.data_imposicao
                                    else ""
                                ),
                                "cumprimento": True if sj.cumprimento == 1 else False,
                                "dataCumprimento": (
                                    sj.data_cumprimento.strftime("%Y-%m-%d")
                                    if sj.data_cumprimento
                                    else ""
                                ),
                                "extincaoPunibilidade": (
                                    True if sj.ext_punibilidade == 1 else False
                                ),
                                "reabilitacao": True if sj.reabilitacao == 1 else False,
                                "dataReabilitacao": (
                                    sj.data_reabilitacao.strftime("%Y-%m-%d")
                                    if sj.data_reabilitacao
                                    else ""
                                ),
                            }
                        )

                    # DADOS DOS MEMBROS
                    membrosProcessos.append(
                        {
                            "membro": "objeto obtemMembros",
                            "situacao": mproc.get_situacao_display()
                            .replace(" ", "_")
                            .replace("â", "a")
                            .replace(":", "")
                            .upper(),
                            "dataSituacao": (
                                mproc.data_situacao.strftime("%Y-%m-%d")
                                if mproc.data_situacao
                                else ""
                            ),
                            "ativo": mproc.ativo,
                            "justificativaExclusao": mproc.justificativa_exclusao,
                            "sancoes": sancoes,
                        }
                    )

                # DADOS DA FASE RECURSAL
                for fr in pj.fase_recursal.all():
                    faseRecursal.append(
                        {
                            "numeroLocal": fr.numero_local,
                            "orgaoJulgador": fr.orgao_julgador,
                            "nomeAcao": fr.nome_acao,
                            "url": fr.url,
                            "ativo": True,
                            "justificativaExclusao": "",
                        }
                    )
                print(pj)

                processo_judicial["membrosProcessos"] = membrosProcessos
                processo_judicial["faseRecursal"] = faseRecursal

                processos_judiciais.append(processo_judicial)
                try:
                    print(processos_judiciais)
                    # member_added = cliente_membro_processo.service.salvarProcessosJudiciais(usuario, senha, processos_judiciais)
                except Exception as e:
                    print(e)
            except Exception:
                print("NAO ENVIADO")
