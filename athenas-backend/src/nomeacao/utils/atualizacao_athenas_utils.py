from rh.models import (
    PessoaFisica,
    Endereco,
    Telefone,
    Documento,
    DocsDadosEspecificos,
    DadoBancarioPessoa,
)

from contrib.utils import getLogger
from contrib.middleware import get_current_user, set_current_user

from nomeacao.utils.utils import (
    normalizar_cpf,
    normalizar_nome_social,
    buscar_uf,
    normalizar_rg_orgao,
    buscar_tipo_endereco_choice,
    buscar_tipo_logr_choice,
    buscar_municipio,
    buscar_tipo_tel_choice,
    normalizar_data_str_date,
    buscar_banco,
    normalizar_tipo_conta,
    buscar_dados_bancarios,
)

from rh.const import CNH, CNH_CATEGORIA

log = getLogger(__name__)


def atualizar_cadastro_pf_athenas(q_pf_athenas, pf_convidado):
    q_pf_athenas.update(
        nome=normalizar_nome_social(pf_convidado),
        social_name=pf_convidado.nome_completo,
        data_nascimento=pf_convidado.dt_nascimento,
        raca_cor=pf_convidado.cor,
        email_pessoal=pf_convidado.email,
        sexo=pf_convidado.sexo.upper(),
        sexual_orientation=pf_convidado.orientacao_sexual,
        genero=pf_convidado.identidade_genero,
        sangue=pf_convidado.sangue_tipo,
        fator_rh=pf_convidado.sangue_fator_rh,
        doador=pf_convidado.sangue_doador,
        nome_mae=pf_convidado.filiacao_mae[0:80] if pf_convidado.filiacao_mae else "",
        nome_pai=pf_convidado.filiacao_pai[0:80] if pf_convidado.filiacao_pai else "",
        rg=pf_convidado.documentacao.rg,
        rg_orgao=normalizar_rg_orgao(pf_convidado.documentacao.rg_orgao),
        rg_data_expedicao=pf_convidado.documentacao.rg_data,
        rg_uf=buscar_uf(pf_convidado.documentacao.rg_uf),
    )


def criar_cadastro_pf_athenas(pf_convidado):
    usuario = get_current_user()
    if usuario is None:
        set_current_user("athenas")
        usuario = get_current_user()

    pf_athenas = PessoaFisica.objects.create(
        cpf=normalizar_cpf(pf_convidado.documentacao.cpf),
        nome=normalizar_nome_social(pf_convidado),
        social_name=pf_convidado.nome_completo,
        data_nascimento=pf_convidado.dt_nascimento,
        raca_cor=pf_convidado.cor,
        email_pessoal=pf_convidado.email,
        sexo=pf_convidado.sexo.upper(),
        sexual_orientation=pf_convidado.orientacao_sexual,
        genero=pf_convidado.identidade_genero,
        sangue=pf_convidado.sangue_tipo,
        fator_rh=pf_convidado.sangue_fator_rh,
        doador=pf_convidado.sangue_doador,
        nome_mae=pf_convidado.filiacao_mae[0:80] if pf_convidado.filiacao_mae else "",
        nome_pai=pf_convidado.filiacao_pai[0:80] if pf_convidado.filiacao_pai else "",
        rg=pf_convidado.documentacao.rg,
        rg_orgao=normalizar_rg_orgao(pf_convidado.documentacao.rg_orgao),
        rg_data_expedicao=pf_convidado.documentacao.rg_data,
        rg_uf=buscar_uf(pf_convidado.documentacao.rg_uf),
    )

    return pf_athenas


def apagar_cnh_pf_athenas(cnh):
    cnh.delete()


def criar_cadastro_cnh_pf_athenas(pf_convidado_documentacao, pf_athenas):
    uf = buscar_uf(pf_convidado_documentacao.cnh_uf)

    dado_especifico = DocsDadosEspecificos.objects.create(
        especificidade=CNH_CATEGORIA,  # 4 - CNH CATEGORIA
        valor=pf_convidado_documentacao.cnh_categoria,
    )

    dt_exp = normalizar_data_str_date(pf_convidado_documentacao.cnh_data_exp, "-")
    dt_val = normalizar_data_str_date(pf_convidado_documentacao.cnh_data_val, "-")

    if uf is not None and dt_exp is not None and dt_val is not None:
        doc_cnh = Documento.objects.create(
            natural_person=pf_athenas,
            tipo_documento=CNH,
            numero=pf_convidado_documentacao.cnh_numero,
            estado_expedicao=uf,
            data_expedicao=dt_exp,
            data_validade=dt_val,
        )

        doc_cnh.dados_especificos.add(dado_especifico)
        pf_athenas.documento.add(doc_cnh)


def criar_endereco_athenas(pf_athenas, pf_convidado):
    tipo_endereco_choice = buscar_tipo_endereco_choice(
        pf_convidado.endereco.tipo_endereco
    )
    if tipo_endereco_choice is None:
        log.info(
            f">>> Tipo de endereço inválido para: {pf_convidado} - tipo: {pf_convidado.endereco.tipo_endereco}"
        )
        return None

    tipo_logr_choice = buscar_tipo_logr_choice(pf_convidado.endereco.tipo_logradouro)
    if tipo_logr_choice is None:
        log.info(
            f">>> Tipo de logradouro inválido para: {pf_convidado} - tipo: {pf_convidado.endereco.tipo_logradouro}"
        )
        return None

    municipio = buscar_municipio(pf_convidado.endereco.municipio_id)

    Endereco.objects.get_or_create(
        tipo_endereco=tipo_endereco_choice,
        tipo_logradouro=tipo_logr_choice,
        municipio=municipio,
        cep=pf_convidado.endereco.cep,
        logradouro=pf_convidado.endereco.logradouro,
        numero=pf_convidado.endereco.numero,
        bairro=pf_convidado.endereco.bairro,
        complemento=pf_convidado.endereco.compl,
        person=pf_athenas,
    )


def criar_tel_athenas(pf_athenas, pf_convidado):
    tipo_tel = buscar_tipo_tel_choice()

    Telefone.objects.get_or_create(
        tipo_telefone=tipo_tel,
        numero=pf_convidado.tel_cel,
        person=pf_athenas,
    )


def criar_dados_bancarios_athenas(pf_athenas, pf_convidado):
    banco = buscar_banco(pf_convidado.dados_bancarios.banco)
    tipo_conta = normalizar_tipo_conta(pf_convidado.dados_bancarios.tipo_conta)

    if banco is not None and tipo_conta is not None:
        num_agencia = pf_convidado.dados_bancarios.numero_agencia.replace("-", "")
        num_conta = pf_convidado.dados_bancarios.numero_conta.replace("-", "")

        q_dados_bancarios = buscar_dados_bancarios(
            pf_athenas, banco, tipo_conta, num_agencia, num_conta
        )
        if q_dados_bancarios.exists() is False:
            if pf_athenas.dadosbancarios.exists():
                pf_athenas.dadosbancarios.update(principal=False)

            DadoBancarioPessoa.objects.create(
                pessoa=pf_athenas,
                principal=True,
                banco=banco,
                tipo_conta=tipo_conta,
                agencia=num_agencia,
                conta_corrente_completa=num_conta,
            )
        elif q_dados_bancarios.exists() and q_dados_bancarios.filter(principal=False):
            pf_athenas.dadosbancarios.update(principal=False)
            q_dados_bancarios.update(principal=True)
