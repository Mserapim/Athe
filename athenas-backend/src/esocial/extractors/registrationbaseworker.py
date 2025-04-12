# -.- coding: utf-8 -.-
from django.db.models import Q
from django.template.defaultfilters import striptags

from contrib.daterange import NewDateRange
from contrib.utils import getLogger
from esocial.const import MARITAL_STATUS_MAP, RACE_MAP
from esocial.extractors.base import ConfigReference, Extractor
from esocial.extractors.dependent import DependentExtractor
from esocial.managers.file_support import get_register_model
from esocial.models import ItemTable
from esocial.utils import esocial_environment
from rh.const import AUDITIVE, INTELLECTUAL, MAP_FORESIGHT, MENTAL, PHYSICAL, VISUAL
from rh.gfp.models import Periodo
from rh.models import Dependencia as RhDependencia
from rh.models import NaturalPersonHistory, PessoaFisica, SocialSecurityEmployee

log = getLogger(__name__)


MAP_FORESIGHT = {1: 1, 2: 2, 3: 2}  # RGPS  # RPPS


class WorkerBaseExtractor(Extractor):

    @classmethod
    def _get_extract_model(cls, extract_model=None):
        """Este método retorna o modelo que será extraído. Utilizando EXTRACTED_CLASS, ou get_register_model do extrator.

        Args:
            extract_model (Event): Event. Defaults to None.

        Returns:
            Event: Event
        """
        if not extract_model:
            extract_model = cls.EXTRACTED_CLASS
        if not extract_model:
            extract_model = get_register_model(
                ((cls.__name__).upper())
                .replace("EXTRACTOR", "")
                .replace("TRAINEE", "")
                .replace("REQUESTED", "")
                .lower()
            )

        return extract_model

    def acronym(self):
        if not self._acronym:
            self._acronym = (
                self.__class__.__name__.lower()
                .replace("extractor", "")
                .replace("trainee", "")
                .replace("requested", "")
            )
        return self._acronym

    @classmethod
    def _get_oid(cls, instance_outside, **kwargs):
        """Este método retorna a definição do OID do instance_outside. Por padrão é instance_outside.pk.

        Returns:
            oid (int): default é instance_outside.pk
        """
        return instance_outside.matricula

    @classmethod
    def _cr_history(cls, instance_outside):
        return ConfigReference(
            queryset=PessoaFisica.objects.filter(pk=instance_outside.pessoa_fisica.pk),
            start_validity_field="data_alteracao_esocial",
        )

    @classmethod
    def _cr_dependency(cls, instance_outside):
        return ConfigReference(
            queryset=RhDependencia.objects.filter(tipo__in=(1, 3)).filter(
                dependente__servidor__pk=instance_outside.pk
            ),
            start_validity_field="data_inicio",
            end_validity_field="data_fim",
        )

    def last_period(self):
        return Periodo.objects.filter(
            ano=self.start_validity().year, mes=self.start_validity().month
        ).last()

    def trabalhador_cpf_trab(self, instance_outside=None):
        """Preencher com o número do CPF do trabalhador. Validação: Deve ser um CPF válido."""
        natural_person = self._instance_outside.pessoa_fisica
        if instance_outside:
            natural_person = instance_outside
        return natural_person.cpf[:11]

    def trabalhador_nm_trab(self, instance_outside=None):
        """Nome do Trabalhador. Validação: Deve ser um nome válido."""
        if instance_outside:
            return f"{instance_outside.nome}"
        return f"{self._instance_outside.pessoa_fisica.nome}"

    def trabalhador_sexo(self, instance_outside=None):
        """Sexo do Trabalhador:
          M - Masculino;
          F - Feminino.
        Valores Válidos: M, F."""
        natural_person = self._instance_outside.pessoa_fisica
        if instance_outside:
            natural_person = instance_outside
        return natural_person.sexo

    def trabalhador_raca_cor(self, instance_outside=None):
        """Raça e cor do trabalhador, conforme opções abaixo:
          1 - Branca;
          2 - Negra;
          3 - Parda (parda ou declarada como mulata, cabocla,
        cafuza, mameluca ou mestiça de negro com pessoa de outra cor ou raça);
          4 - Amarela (de origem japonesa, chinesa, coreana etc);
          5 - Indígena;
          6 - Não informado. Valores Válidos: 1, 2, 3, 4, 5, 6."""
        natural_person = self._instance_outside.pessoa_fisica
        if instance_outside:
            natural_person = instance_outside
        return RACE_MAP.get(natural_person.raca_cor)

    def trabalhador_est_civ(self, instance_outside=None):
        """Estado civil do trabalhador, conforme opções abaixo:
          1 - Solteiro;
          2 - Casado;
          3 - Divorciado;
          4 - Separado;
          5 - Viúvo.
        Valores Válidos: 1, 2, 3, 4, 5."""
        natural_person = self._instance_outside.pessoa_fisica
        if instance_outside:
            natural_person = instance_outside
        return MARITAL_STATUS_MAP.get(natural_person.estado_civil)

    def trabalhador_grau_instr(self, instance_outside=None):
        """Grau de instrução do trabalhador, conforme opções abaixo:
          01 - Analfabeto, inclusive o que, embora tenha recebido instrução, não se alfabetizou;
          02 - Até o 5º ano incompleto do Ensino Fundamental (antiga 4ª série) ou que se tenha alfabetizado
          sem ter frequentado escola regular;
          03 - 5º ano completo do Ensino Fundamental;
          04 - Do 6º ao 9º ano do Ensino Fundamental incompleto (antiga 5ª a 8ª série);
          05 - Ensino Fundamental Completo;06 - Ensino Médio incompleto;
          07 - Ensino Médio completo;
          08 - Educação Superior incompleta;
          09 - Educação Superior completa;
          10 - Pós-Graduação completa;
          11 - Mestrado completo;
          12 - Doutorado completo.
        Valores Válidos: 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12."""
        natural_person = self._instance_outside.pessoa_fisica
        if instance_outside:
            natural_person = instance_outside

        code = "05"
        try:
            code = ItemTable.objects.by_choice_table(
                natural_person.grau_instrucao, "99"
            ).code
        except Exception as err:
            log.exception(err)
            log.info(
                f"{natural_person} - grau_instrucao: {natural_person.grau_instrucao}"
            )
        return code

    def trabalhador_nm_soc(self, instance_outside=None):
        """Nome social para travesti ou transexual."""
        natural_person = self._instance_outside.pessoa_fisica
        if instance_outside:
            natural_person = instance_outside

        if not natural_person.social_name:
            return None
        social_name = (
            natural_person.social_name
            if natural_person.social_name != natural_person.nome
            else None
        )
        return social_name

    def nascimento_dt_nascto(self, instance_outside=None):
        "Preencher com a data de nascimento."
        natural_person = self._instance_outside.pessoa_fisica
        if instance_outside:
            natural_person = instance_outside
        return natural_person.data_nascimento

    def nascimento_pais_nascto(self, instance_outside=None):
        """Preencher com o código do país de nascimento do trabalhador,
        conforme tabela 6.
        Validação: Deve ser um código existente na tabela 6."""
        natural_person = self._instance_outside.pessoa_fisica
        if instance_outside:
            natural_person = instance_outside
        return (
            str(natural_person.municipio_naturalidade.estado.pais.esocial_code)
            if natural_person.municipio_naturalidade
            else None
        )

    def nascimento_pais_nac(self, instance_outside=None):
        """Preencher com o código do país de nacionalidade do trabalhador, conforme tabela 6.
        Validação: Deve ser um código existente na tabela."""
        natural_person = self._instance_outside.pessoa_fisica
        if instance_outside:
            natural_person = instance_outside

        value = None
        if natural_person.nationality:
            value = str(natural_person.nationality.esocial_code)
        return value

    def brasil_tp_lograd(self, instance_outside=None):
        """Tipo de Logradouro, conforme tabela 20.
        Validação: Deve ser um código válido, existente na tabela 20."""
        natural_person = self._instance_outside.pessoa_fisica
        if instance_outside:
            natural_person = instance_outside
        return type_street(natural_person)

    def brasil_dsc_lograd(self, instance_outside=None):
        """Descrição do logradouro."""
        value = None
        if instance_outside:
            value = instance_outside.logradouro
        else:
            ad = address(self._instance_outside.pessoa_fisica)
            value = ad.logradouro if ad else None
        return (value[:80]).lstrip() if value else None

    def brasil_nr_lograd(self, instance_outside=None):
        """Número do logradouro.  Se não houver número a ser informado, preencher com S/N."""
        if instance_outside:
            return (
                instance_outside.numero[:10] if instance_outside.numero else None
            ) or "S/N"

        ad = address(self._instance_outside.pessoa_fisica)
        return (ad.numero[:10] if ad.numero else None) or "S/N" if ad else None

    def brasil_complemento(self, instance_outside=None):
        """Complemento do logradouro."""
        value = None
        if instance_outside:
            value = instance_outside.complemento
        else:
            ad = address(self._instance_outside.pessoa_fisica)
            value = ad.complemento if ad and ad.complemento else None

        if value:
            value = striptags(value)[0:30]
            if len(value) == 0 or value.isspace():
                value = None
        return value

    def brasil_bairro(self, instance_outside=None):
        """Nome do bairro/distrito."""
        if instance_outside:
            return instance_outside.bairro

        ad = address(self._instance_outside.pessoa_fisica)
        return ad.bairro if ad and ad.bairro else None

    def brasil_cep(self, instance_outside=None):
        """Código de Endereçamento Postal - CEP.
        Validação: Deve ser preenchido apenas com números.
        Deve ser um CEP válido."""
        value = None
        if instance_outside:
            # value = (''.join(filter(str.isdigit, str(instance_outside.cep))))[0:8]
            value = instance_outside.cep
        else:
            ad = address(self._instance_outside.pessoa_fisica)
            value = ad.cep if ad else None

        return ("".join(filter(str.isdigit, str(value))))[0:8] if value else value

    def brasil_cod_munic(self, instance_outside=None):
        """Preencher com o código do município, conforme tabela do IBGE
        Validação: Deve ser um código existente na tabela do IBGE."""
        if instance_outside:
            return instance_outside.municipio.ibge

        ad = address(self._instance_outside.pessoa_fisica)
        return ad.municipio.ibge if ad and ad.municipio.ibge else None

    def brasil_uf(self, instance_outside=None):
        """Preencher com a sigla da Unidade da Federação
        Validação: Deve ser uma UF válida."""
        if instance_outside:
            return instance_outside.municipio.estado.sigla

        ad = address(self._instance_outside.pessoa_fisica)
        return ad.municipio.estado.sigla if ad else None

    def exterior_pais_resid(self, instance_outside=None):
        """Preencher com o código do país, conforme tabela 6.
        Validação: Deve ser um código existente na tabela."""
        if instance_outside:
            return str(instance_outside.country.esocial_code)

        ad = address(self._instance_outside.pessoa_fisica, exclude_outsider=False)
        return str(ad.country.esocial_code) if ad else None

    def exterior_dsc_lograd(self, instance_outside=None):
        """Descrição do logradouro."""
        value = None
        if instance_outside:
            value = instance_outside.logradouro[:80]
        else:
            ad = address(self._instance_outside.pessoa_fisica, exclude_outsider=False)
            value = ad.logradouro[:80] if ad else None

        return value[:80] if value else value

    def exterior_nr_lograd(self, instance_outside=None):
        """Número do logradouro. Se não houver número a
        ser informado, preencher com S/N."""
        if instance_outside:
            return (
                instance_outside.numero[:10] if instance_outside.numero else None
            ) or "S/N"

        ad = address(self._instance_outside.pessoa_fisica, exclude_outsider=False)
        return (ad.numero[:10] if ad.numero else None) or "S/N" if ad else None

    def exterior_complemento(self, instance_outside=None):
        """Complemento do logradouro."""
        value = None
        if instance_outside:
            value = instance_outside.complemento
        else:
            ad = address(self._instance_outside.pessoa_fisica, exclude_outsider=False)
            value = ad.complemento if ad else None

        if value:
            value = striptags(value)[0:30]
            if len(value) == 0 or value.isspace():
                value = None
        return value

    def exterior_bairro(self, instance_outside=None):
        """Nome do bairro/distrito."""
        if instance_outside:
            return instance_outside.bairro

        ad = address(self._instance_outside.pessoa_fisica, exclude_outsider=False)
        return ad.bairro if ad else None

    def exterior_nm_cid(self, instance_outside=None):
        """Nome da Cidade."""
        if instance_outside and instance_outside.municipio:
            return instance_outside.municipio.nome

        ad = address(self._instance_outside.pessoa_fisica, exclude_outsider=False)
        return ad.outsider_citty if ad else None

    def exterior_cod_postal(self, instance_outside=None):
        """Código de Endereçamento Postal."""
        if instance_outside:
            return instance_outside.cep

        ad = address(self._instance_outside.pessoa_fisica, exclude_outsider=False)
        return ad.cep if ad else None

    def trab_imig_tmp_resid(self, instance_outside=None):
        natural_person = self._instance_outside.pessoa_fisica
        if instance_outside:
            natural_person = instance_outside
        return (
            natural_person.immigrant_residence_time
            if natural_person.immigrant_residence_time != 10
            else None
        )

    def trab_imig_cond_ing(self, instance_outside=None):
        natural_person = self._instance_outside.pessoa_fisica
        if instance_outside:
            natural_person = instance_outside
        return (
            natural_person.immigrant_entry_condition
            if natural_person.immigrant_entry_condition != 10
            else None
        )

    def info_deficiencia_def_fisica(self):
        """Deficiência Física:
          S - Sim;
          N - Não.
        Valores Válidos: S, N."""
        return (
            "S"
            if self._instance_outside.pessoa_fisica.necessidades_especiais.filter(
                deficiency_type=PHYSICAL
            ).exists()
            else "N"
        )

    def info_deficiencia_def_visual(self):
        """Deficiência visual:
          S - Sim;
          N - Não.
        Valores Válidos: S, N."""
        return (
            "S"
            if self._instance_outside.pessoa_fisica.necessidades_especiais.filter(
                deficiency_type=VISUAL
            ).exists()
            else "N"
        )

    def info_deficiencia_def_auditiva(self):
        """Deficiência auditiva:
          S - Sim;
          N - Não.
        Valores Válidos: S, N."""
        return (
            "S"
            if self._instance_outside.pessoa_fisica.necessidades_especiais.filter(
                deficiency_type=AUDITIVE
            ).exists()
            else "N"
        )

    def info_deficiencia_def_mental(self):
        """Deficiência Mental:
          S - Sim;
          N - Não.
        Valores Válidos: S, N."""
        return (
            "S"
            if self._instance_outside.pessoa_fisica.necessidades_especiais.filter(
                deficiency_type=MENTAL
            ).exists()
            else "N"
        )

    def info_deficiencia_def_intelectual(self):
        """Deficiência Intelectual:
          S - Sim;
          N - Não.
        Valores Válidos: S, N."""
        return (
            "S"
            if self._instance_outside.pessoa_fisica.necessidades_especiais.filter(
                deficiency_type=INTELLECTUAL
            ).exists()
            else "N"
        )

    def info_deficiencia_reab_readap(self):
        """Informar se o trabalhador é reabilitado (empregado) ou readaptado
        (servidor público/militar). Reabilitado: estando o empregado incapacitado
        parcial ou totalmente para o trabalho, cumpriu Programa de Reabilitação
        Profissional no INSS, recebendo certificado, sendo proporcionado os meios
        indicados para participar do mercado de trabalho. Readaptado: o servidor
        está investido emcargo de atribuições e responsabilidades compatíveis com
        a limitação que tenha sofrido em sua capacidade física ou mental verificada
        em inspeção médica:
          S - Sim;
          N - Não.
        Valores Válidos: S, N."""
        result = (
            self._instance_outside.pessoa_fisica.deficiencyinformation.rehabilitation
            if hasattr(self._instance_outside.pessoa_fisica, "deficiencyinformation")
            else None
        )
        return "S" if result else "N"

    def info_deficiencia_observacao(self):
        result = (
            self._instance_outside.pessoa_fisica.deficiencyinformation.note
            if hasattr(self._instance_outside.pessoa_fisica, "deficiencyinformation")
            else None
        )
        return result

    def dependente(self):
        """Informações dos dependentes da pessoa física."""
        # FIXME: PRECISAMOS INDICAR QUANDO HOUVE MUDANÇA DO TIPO, POIS A DATA DE INÍCIO DELE NÃO FARÁ MAIS PARTE DA LISTA DA ALTERAÇÕES
        # FIXME: PRECISAMOS CRIAR O MODELO QUE VAI INDICAR A DATA EM QUE OCORREU A SAÍDA DE ALGUM OBJETO
        start_date = self.start_validity()
        if start_date < self.initial_group_date():
            start_date = self.initial_group_date()
        dependents = []
        query = (
            RhDependencia.objects.filter(dependente__servidor=self._instance_outside)
            .active_in(range=NewDateRange(start_date, start_date))
            .esocial_valid()
        )
        if esocial_environment() == 2:
            query = query.exclude(
                Q(dependente__pessoa_fisica__cpf__isnull=True)
                | Q(dependente__pessoa_fisica__cpf="")
            )
        for dependency in query.distinct("dependente"):
            extractor = DependentExtractor(dependency.dependente, extractor_base=self)
            extractor.extract_fields()
            dependents.append(extractor._extracted_fields_json)
        return dependents

    def contato_fone_princ(self, instance_outside=None):
        """Número de telefone do trabalhador, com DDD.
        Validação: Se preenchido, deve conter apenas números, com o
        mínimo de dez dígitos."""
        value = None
        if instance_outside:
            value = instance_outside.phone_main
        else:
            phone = self._instance_outside.pessoa_fisica.phone.filter(main=True)
            value = phone.last().numero if phone.exists() else None

        return ("".join(filter(str.isdigit, str(value))))[:13] if value else value

    def contato_email_princ(self, instance_outside=None):
        """Endereço eletrônico.
        Validação: O e-mail deve ser possuir o caractere @ e este não
        pode estar no início e no fim do e-mail. Deve possuir no mínimo
        um caractere . depois do@ e não pode estar no início ou no final
        do e-mail."""
        natural_person = self._instance_outside.pessoa_fisica
        if instance_outside:
            natural_person = instance_outside
        return (
            natural_person.email_institucional.lower()
            if natural_person.email_institucional
            else None
        )

    def vinculo_matricula(self):
        return str(self._instance_outside.matricula)

    @classmethod
    def _vinculo_tp_reg_trab(cls):
        # TODO: Verificar se é possível identificar o tipo de regime de trabalho A PARTIR DA CONFIGURAÇÃO PREVIDENCIÁRIA
        return 2

    def vinculo_tp_reg_trab(self):
        return self._vinculo_tp_reg_trab()

    def vinculo_tp_reg_prev(self):
        return vinculo_tp_reg_prev(
            self._instance_outside,
            self._start_validity,
            self._end_validity,
            self.initial_group_date(),
        )

    def vinculo_cad_ini(self):
        return (
            "S"
            if self.start_validity()
            < self.configuration.initial_date_non_periodic_events
            else "N"
        )

    def info_celetista_dt_adm(self):
        return None

    def info_celetista_tp_admissao(self):
        return None

    def info_celetista_ind_admissao(self):
        return None

    def info_celetista_tp_reg_jor(self):
        return None

    def info_celetista_nat_atividade(self):
        return None

    def info_celetista_dt_base(self):
        return None

    def info_celetista_cnpj_sind_categ_prof(self):
        return None

    def fgts_dt_opc_fgts(self):
        return None

    def trab_temporario_hip_leg(self):
        return None

    def trab_temporario_just_contr(self):
        return None

    def ide_estab_vinc_tp_insc(self):
        return None

    def ide_estab_vinc_nr_insc(self):
        return None

    def ide_trab_substituido_cpf_trab_subst(self):
        return None

    def aprend_tp_insc(self):
        return None

    def aprend_nr_insc(self):
        return None

    def social_security_employee(self):
        return social_security_employee(
            self._instance_outside,
            self._start_validity,
            self._end_validity,
            self.initial_group_date(),
        )


def social_security_employee(
    employee, start_validity=None, end_validity=None, initial_group_date=None
):
    validity = start_validity
    if end_validity and end_validity < initial_group_date:
        validity = end_validity
    if validity:
        return (
            SocialSecurityEmployee.objects.currents_in(
                range=NewDateRange(validity, validity)
            )
            .filter(employee=employee)
            .last()
        )
    return None


def vinculo_tp_reg_prev(
    employee, start_validity=None, end_validity=None, initial_group_date=None
):
    value = None
    if employee.is_occasional_collaborator:
        """Colaborador Eventual possui RPPS como default."""
        value = MAP_FORESIGHT.get(2)
        if SocialSecurityEmployee.objects.filter(
            employee=employee, social_security_config=1
        ).exists():
            value = MAP_FORESIGHT.get(1)
    else:
        ss = social_security_employee(
            employee, start_validity, end_validity, initial_group_date
        )
        if ss and ss.social_security_config.regime:
            value = MAP_FORESIGHT.get(ss.social_security_config.regime)
    return value


def address(person, exclude_outsider=True):
    return person.address.exclude(outsider=exclude_outsider).last()


def type_street(*args):
    _address = args[0]
    if isinstance(args[0], PessoaFisica):
        _address = address(args[0])

    code = None
    try:
        if _address:
            code = ItemTable.objects.by_choice_table(
                _address.tipo_logradouro, "20"
            ).code
    except Exception as err:
        log.exception(err)
    return code
