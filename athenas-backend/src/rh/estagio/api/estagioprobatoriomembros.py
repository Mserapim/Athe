from datetime import datetime
from contrib.newrest import RestfulDRY
from contrib.utils import getLogger
from rh.models import Servidor

from rh.afastamento.models import BaseLicencaAfastamento

log = getLogger(__name__)


class MembersProbationaryPhase(RestfulDRY):
    """
    API para listar todos os "membros Substitutos".
    """

    _model = Servidor

    full_text_index = (
        "pessoa_fisica__nome__icontains",
        "pessoa_fisica__cpf__iexact",
        "matricula__iexact",
    )

    def json(self, *args):
        """
        Responde com um JSON com a nova instância do Widget.

        :param args Argumentos repassados pela URL.
        """
        self.response["content-type"] = "text/javascript"
        self.response.write('Ext._create("estagio.members_probationary_phase.Manage")')

    def get_job_positions_member_in_probationary_phase(self, query):
        """
        Função que retorna uma lista contendo pks de cargos cujos membros
        estão em estágio probatório.

        :returns: list: lista com pks de cargos dos membros em estágio probatório
        """
        result_list = []
        for item in query:
            if item.member_substitute:
                result_list.append(item.pk)
        return result_list

    def get_query(self):
        """
        Método sobrescrito que retorna uma QuerySet dos Membros em estágio probatório

        :returns: QuerySet: QuerySet
        """
        query = (
            super()
            .get_query()
            .filter(
                type_by_possession__in=[
                    "MBR",
                    "MEL",
                    "MCM",
                    "MEC",
                    "MBR2",
                    "MEL2",
                    "MCM2",
                    "MEC2",
                    "MAP",
                ],
                ativo=True,
            )
        )
        return query.filter(
            pk__in=self.get_job_positions_member_in_probationary_phase(query)
        )

    def model_to_dict(self, instance):
        """
        Cria um dicionário com atributos de uma instância.

        :param instance: Instância de Model.

        :returns: Dicionário com indices pk e unicode da instância.
        """
        dict_model = {}
        dict_model.update(
            pk=instance.pk,
            name=instance.pessoa_fisica.nome,
            matricula=instance.matricula,
            job_role=instance.job_position().cargo.nome,
            first_possession_date=instance.first_possession_date.strftime("%d/%m/%Y"),
            exercise_date=instance.data_exercicio.strftime("%d/%m/%Y"),
            worked_days=instance.get_worked_days_if_employee_be_in_probationary_phase,
            absence_days=instance.get_days_departure,
            complete_phase_date=instance.date_when_complete_the_probationary_phase().strftime(
                "%d/%m/%Y"
            ),
            days_for_complete_phase=instance.days_for_complete_the_probationary_phase(),
            workplace=str(instance.workplace_current),
        )
        return dict_model


class MembroProbatorioAfastamentosRESTFUL(RestfulDRY):
    """
    API para listar os afastamentos de um  Membro.
    """

    _model = BaseLicencaAfastamento

    def json(self, args=[]):
        self.response["content-type"] = "text/javascript"
        self.response.write(
            'Ext._create("estagio.members_probationary_phase.afastamentos.Manage")'
        )

    def get_query(self):
        """
        Método sobrescrito que retorna uma QuerySet dos afastamentos de um  Membro em estágio probatório

        :returns: QuerySet: QuerySet
        """
        membro_id = self.request.REQUEST.get("membroId")
        try:
            membro = Servidor.objects.get(id=membro_id)
        except:
            return []

        return self.buscar_afastamentos(membro)

    def buscar_afastamentos(self, instance):
        return instance.departures(
            start_date=instance.first_possession_date,
            end_date=datetime.now().date(),
        )

    def model_to_dict(self, instance):
        params = super(MembroProbatorioAfastamentosRESTFUL, self).model_to_dict(
            instance
        )
        params.update(
            {
                "tipo": instance.get_tipo_display(),
                "qtd_dias": instance.days_amount,
                "servidor_unicode": f"{instance.servidor.matricula} - {instance.servidor.pessoa_fisica.social_name}",
            }
        )

        return params
