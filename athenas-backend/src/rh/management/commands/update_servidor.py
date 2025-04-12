# -*- coding: utf-8 -*-
import inspect

from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Q

from contrib.middleware import set_current_user
from contrib.utils import getLogger
from rh.gfp.models import MovimentacaoProgressao
from rh.utils import feature_flag_arquimedes, FeatureFlagDisabledError
from rh.afastamento.models import BaseLicencaAfastamento
from rh.models import (
    DeclaracaoAtividade,
    MovimentacaoRequisicao,
    MovimentacaoSubstituicao,
    Servidor,
    ServidorLotacao,
    SituacaoFuncional,
    WorkplaceExerciseHistory,
)

log = getLogger("db")


class Command(BaseCommand):
    verbose = "False"
    help = """"""

    def _add_arquimedes_arguments(self, parser):
        parser.add_argument(
            "-x",
            "--update_arquimedes_desig",
            action="store_true",
            dest="update_arquimedes_desig",
            help="Atualiza as designações do arquimedes com o exercício do athenas.",
        )
        parser.add_argument(
            "-i",
            "--arquimedes_inactivate",
            action="store",
            default=True,
            dest="arquimedes_inactivate",
            type=str,
            help="Inativa exercícios no arquimedes.(id separado por ',': 1,2,3)",
        )

    def add_arguments(self, parser):
        parser.add_argument(
            "-r",
            "--movrequisicao",
            action="store_true",
            dest="movrequisicao",
            help="Realiza procedimentos relacionados à MovimentacaoRequisicao.",
        )
        parser.add_argument(
            "-s",
            "--servidor",
            action="store_true",
            dest="servidor",
            help="Verifica se o servidor está em exercício.",
        )
        parser.add_argument(
            "-t",
            "--situacao",
            action="store_true",
            dest="situacao",
            help="Atualiza situação funcional do servidor.",
        )
        parser.add_argument(
            "-a",
            "--afastamento",
            action="store_true",
            dest="afastamento",
            help="Atualiza estado dos afastamentos.",
        )
        parser.add_argument(
            "-m",
            "--movsubs",
            action="store_true",
            dest="movsubs",
            help="Realiza procedimentos relacionados à MovimentacaoSubstituicao.",
        )
        parser.add_argument(
            "-d",
            "--declaration",
            action="store_true",
            dest="declaration",
            help="Atualiza ativo das Declarações de Atividade.",
        )
        parser.add_argument(
            "-w",
            "--workplacehistory",
            action="store_true",
            dest="workplacehistory",
            help="Atualiza ativo das Declarações de Atividade.",
        )

    def __init__(self, *args, **kargs):
        BaseCommand.__init__(self, *args, **kargs)

    def _get_datetime(self):
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def _print_arquimedes_error(self, error):
        msg = f"[{self._get_datetime()}] {str(error)}"
        log.warning(msg)
        print(msg)

    def _handle_arquimedes_options(self, **options):
        if options["update_arquimedes_desig"]:
            try:
                self.update_arquimedes_desig()
            except FeatureFlagDisabledError as e:
                self._print_arquimedes_error(e)
        if options["arquimedes_inactivate"]:
            values = options["arquimedes_inactivate"]
            values = values.split(",") if values is not True else []
            try:
                self.arquimedes_inactivate(values)
            except FeatureFlagDisabledError as e:
                self._print_arquimedes_error(e)

    def set_user_to_job(self, username: str) -> None:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            log.error(f'Não foi localizado o usuário "{username}" - {e}')
            set_current_user(User.objects.get(username="athenas"))
        else:
            set_current_user(user)

    def handle(self, *args, **options):
        if options["movrequisicao"]:
            self.set_user_to_job(
                "job_update_servidor_procedimento_movimentacao_requisicao"
            )
            self.procedimento_movimentacao_requisicao()
        if options["servidor"]:
            self.set_user_to_job("job_update_servidor_servidor_exercicio")
            self.servidor_exercicio()

            self.set_user_to_job("job_update_servidor_atualizar_servidor_lotacao")
            self.atualizar_servidor_lotacao()

            self.set_user_to_job("job_update_servidor_atualizar_servidor_progressao")
            self.atualizar_servidor_progressao()
        if options["situacao"]:
            self.set_user_to_job("job_update_servidor_situacao_funcional")
            self.situacao_funcional()
        if options["afastamento"]:
            self.set_user_to_job("job_update_servidor_afastamento")
            self.afastamento()
        if options["movsubs"]:
            self.set_user_to_job(
                "job_update_servidor_atualizar_movimentacao_substituicao"
            )
            self.atualizar_movimentacao_substituicao()
        if options["declaration"]:
            self.set_user_to_job("job_update_servidor_declaration")
            self.declaration()
        if options["workplacehistory"]:
            self.set_user_to_job("job_update_servidor_workplacehistory")
            self.workplacehistory()

    def procedimento_movimentacao_requisicao(self):
        """
        Comando para adicionar e remover Desligamento em
        Posse de Origem para as movimentações de requisição em que o
        período tenha chegado ao fim.
        """
        MovimentacaoRequisicao.execute()

    def servidor_exercicio(self):
        """
        Comando para atualizar a propriedade ativo de cada servidor.
        Utiliza-se is_ativo, pois ele baseia-se na data de exercício.
        """
        log.info("COMANDO -> servidor_exercicio")
        print(
            ">>> [%s] Iniciando atualizacao da propriendade ativo dos servidores >>>>>>>>>>>>>"
            % self._get_datetime()
        )
        for servidor in Servidor.objects.filter():
            ativo_antes = servidor.ativo
            ativo_depois = servidor.is_ativo()
            try:
                if ativo_antes != ativo_depois:
                    servidor.atualiza_cache_ativo()
                    print(
                        (
                            "(%s >> %s) %s " % (ativo_antes, ativo_depois, servidor)
                        ).encode("utf-8")
                    )
                    log.info(
                        "Servidor %s está %s e mudou para %s"
                        % (servidor, ativo_antes, ativo_depois)
                    )
            except Exception as err:
                print(("%s" % err).encode("utf-8"))
                print(
                    (
                        "ERRO: Erro aplicando valor de propriedade ativo. %s (%s >> %s)"
                        % (servidor, ativo_antes, ativo_depois)
                    ).encode("utf-8")
                )
                log.info("Erro aplicando valor de propriedade ativo.")
        print(
            ">>> [%s] Finalizando atualizacao da propriendade ativo dos servidores >>>>>>>>>>>>>"
            % self._get_datetime()
        )

    def situacao_funcional(self):
        SituacaoFuncional.cmd_update_active()
        SituacaoFuncional.update_from_origin()
        SituacaoFuncional._manager_situations()

    def afastamento(self):
        BaseLicencaAfastamento.atualizar_estado()
        self.atualizar_movimentacao_substituicao()
        self.mark_exercise_departure()

    def atualizar_movimentacao_substituicao(self):
        log.info(
            "COMANDO -> atualizar_movimentacao_substituicao(MovimentacaoSubstituicao.call_update_responsible_workplace)"
        )
        MovimentacaoSubstituicao.call_update_responsible_workplace()
        MovimentacaoSubstituicao.cmd_replacement_manager()
        MovimentacaoSubstituicao.update_state()

    def atualizar_servidor_lotacao(self):
        log.info("COMANDO -> LOTAÇÃO: atualizar_servidor_lotacao(atualizar_ativo)")
        ServidorLotacao.cmd_atualizar_ativo()

    def declaration(self):
        DeclaracaoAtividade.cmd_update_active()

    def workplacehistory(self):
        WorkplaceExerciseHistory.cmd_exercise_per_day()

    def mark_exercise_departure(self):
        BaseLicencaAfastamento.mark_exercise_departure()

    def atualizar_servidor_progressao(self):
        MovimentacaoProgressao.cmd_update_lacks_and_suspensions()
