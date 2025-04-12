from contrib.utils import getLogger

from nomeacao.models import (
    PessoaFisicaConvidado,
    DocumentoConvidado,
    EscolaridadeConvidado,
    EnderecoConvidado,
    DadoBancarioConvidado,
)
from nomeacao.cadastramento.models import ConviteNomeacao, AnexoConvite
from rh.models import PessoaFisica

from nomeacao.utils.utils import (
    normalizar_cpf,
    normalizar_sangue_doador,
    normalizar_orientacao_sexual,
    normalizar_tipo_sangue,
    normalizar_fator_rh,
)

from nomeacao.utils.atualizacao_athenas_utils import (
    atualizar_cadastro_pf_athenas,
    criar_cadastro_pf_athenas,
    criar_endereco_athenas,
    criar_tel_athenas,
    criar_cadastro_cnh_pf_athenas,
    apagar_cnh_pf_athenas,
    criar_dados_bancarios_athenas,
)


log = getLogger(__name__)


def criar_pessoa_fisica_convidado(**kwargs):
    nome_completo = kwargs.get("nome_completo", None)
    nome_social = kwargs.get("nome_social", None)

    pessoa = PessoaFisicaConvidado(
        nome_completo=nome_completo.upper() if nome_completo else "",
        nome_social=nome_social.upper() if nome_social else "",
        dt_nascimento=kwargs.get("dt_nascimento"),
        cor=kwargs.get("cor"),
        deficiencia=kwargs.get("deficiencia"),
        tel_cel=kwargs.get("tel_cel"),
        email=kwargs.get("email"),
        sexo=kwargs.get("sexo"),
        orientacao_sexual=normalizar_orientacao_sexual(kwargs.get("orientacao_sexual")),
        identidade_genero=kwargs.get("identidade_genero"),
        cota=kwargs.get("cota"),
        sangue_tipo=normalizar_tipo_sangue(kwargs.get("sangue_tipo")),
        sangue_fator_rh=normalizar_fator_rh(kwargs.get("sangue_fator_rh")),
        sangue_doador=normalizar_sangue_doador(kwargs.get("sangue_doador")),
        filiacao_mae=kwargs.get("filiacao_mae"),
        filiacao_pai=kwargs.get("filiacao_pai"),
    )
    pessoa.save()

    return pessoa


def criar_doc_pessoa_fisica_convidado(convidado, **kwargs):
    documentacao = DocumentoConvidado(
        convidado=convidado,
        rg=kwargs.get("rg"),
        rg_numero=kwargs.get("rg_numero"),
        rg_orgao=kwargs.get("rg_orgao"),
        rg_uf=kwargs.get("rg_uf"),
        rg_data=kwargs.get("rg_data"),
        cnh_numero=kwargs.get("cnh_numero"),
        cnh_uf=kwargs.get("cnh_uf"),
        cnh_categoria=kwargs.get("cnh_categoria"),
        cnh_data_exp=kwargs.get("cnh_data_exp"),
        cnh_data_val=kwargs.get("cnh_data_val"),
        cpf=kwargs.get("cpf"),
        tit_eleit_numero=kwargs.get("tit_eleit_numero"),
        tit_eleit_zona=kwargs.get("tit_eleit_zona"),
        tit_eleit_secao=kwargs.get("tit_eleit_secao"),
        tit_eleit_municipio=kwargs.get("tit_eleit_municipio"),
        tit_eleit_municipio_id=kwargs.get("tit_eleit_municipio_id"),
    )

    documentacao.save()

    return documentacao


def criar_escol_pessoa_fisica_convidado(convidado, **kwargs):
    escolaridade = EscolaridadeConvidado(
        convidado=convidado,
        escolaridade=kwargs.get("escolaridade"),
        coeficiente_graduacao=kwargs.get("coeficiente_graduacao"),
        nome_instituicao_graduacao=kwargs.get("nome_instituicao_graduacao"),
        data_conclusao_graduacao=kwargs.get("data_conclusao_graduacao"),
        nome_instituicao_pos_graduacao=kwargs.get("nome_instituicao_pos_graduacao"),
    )

    escolaridade.save()

    return escolaridade


def criar_ender_pessoa_fisica_convidado(convidado, **kwargs):
    endereco = EnderecoConvidado(
        convidado=convidado,
        tipo_endereco=kwargs.get("tipo_endereco"),
        tipo_logradouro=kwargs.get("tipo_logradouro"),
        logradouro=kwargs.get("logradouro"),
        numero=kwargs.get("numero"),
        compl=kwargs.get("compl"),
        bairro=kwargs.get("bairro"),
        cep=kwargs.get("cep"),
        municipio_id=kwargs.get("municipio_id"),
    )

    endereco.save()

    return endereco


def criar_dados_bancarios_convidado(convidado, **kwargs):
    banco = kwargs.get("banco")
    tipo_conta = kwargs.get("tipo_conta")
    num_ag = kwargs.get("numero_agencia")
    num_conta = kwargs.get("numero_conta")

    if (
        banco not in [None, ""]
        and tipo_conta not in [None, ""]
        and num_ag not in [None, ""]
        and num_conta not in [None, ""]
    ):
        dados_bancarios = DadoBancarioConvidado(
            convidado=convidado,
            banco=banco,
            tipo_conta=tipo_conta,
            numero_agencia=num_ag,
            numero_conta=num_conta,
        )

        dados_bancarios.save()

        return dados_bancarios


def criar_convite_nomeacao(convidado, **kwargs):
    convite = ConviteNomeacao(
        convidado=convidado,
        classificado=kwargs.get("classificado"),
        tipo_nomeacao=kwargs.get("tipo_nomeacao"),
        status_convocacao=kwargs.get("status_convocacao"),
        data_convocacao=kwargs.get("data_convocacao"),
        data_email_convocacao=kwargs.get("data_email_convocacao"),
        data_desistencia=kwargs.get("data_desistencia"),
        data_resposta=kwargs.get("data_resposta"),
        data_possivel_expericao=kwargs.get("data_possivel_expericao"),
        data_expiracao=kwargs.get("data_expiracao"),
    )

    convite.save()

    return convite


def criar_anexo_infos_convite(convite, **kwargs):
    anexo_infos = AnexoConvite(
        convite=convite,
        tipo_documento=kwargs.get("tipo_documento"),
        tipo_documento_descr=kwargs.get("tipo_documento_descr"),
        arquivo_nome=kwargs.get("arquivo_nome"),
        arquivo_nome_original=kwargs.get("arquivo_nome_original"),
        api_relative_path=kwargs.get("api_relative_path"),
        api_diretorio=kwargs.get("api_diretorio"),
    )

    anexo_infos.save()

    return anexo_infos


def cadastrar_convite(tipo_nomeacao, detalhe_cpf):
    pessoa_fisica_convidado = criar_pessoa_fisica_convidado(
        nome_completo=detalhe_cpf["nome_completo"],
        nome_social=detalhe_cpf["nome_social"],
        dt_nascimento=detalhe_cpf["data_nascimento"],
        cor=detalhe_cpf["id_cor"],
        deficiencia=detalhe_cpf["deficiencia"],
        tel_cel=detalhe_cpf["tel_celular"],
        email=detalhe_cpf["email"],
        sexo=detalhe_cpf["sexo"],
        orientacao_sexual=detalhe_cpf["orientacao_sexual"],
        identidade_genero=detalhe_cpf["identidade_genero"],
        cota=detalhe_cpf["cota"],
        sangue_tipo=detalhe_cpf["tipo_sanguineo"],
        sangue_fator_rh=detalhe_cpf["fator_rh"],
        sangue_doador=detalhe_cpf["doador_sangue"],
        filiacao_mae=detalhe_cpf["mae"],
        filiacao_pai=detalhe_cpf["pai"],
    )

    criar_doc_pessoa_fisica_convidado(
        pessoa_fisica_convidado,
        rg=detalhe_cpf["rg"],
        rg_numero=detalhe_cpf["numero_rg"],
        rg_orgao=detalhe_cpf["orgao_rg"],
        rg_uf=detalhe_cpf["uf_rg"],
        rg_data=detalhe_cpf["data_rg"],
        cpf=detalhe_cpf["cpf"],
        cnh_numero=detalhe_cpf["numero_cnh"],
        cnh_uf=detalhe_cpf["uf_cnh"],
        cnh_categoria=detalhe_cpf["categoria_cnh"],
        cnh_data_exp=detalhe_cpf["data_exp_cnh"],
        cnh_data_val=detalhe_cpf["data_val_cnh"],
        tit_eleit_numero=detalhe_cpf["numero_titulo"],
        tit_eleit_zona=detalhe_cpf["zona_eleitoral"],
        tit_eleit_secao=detalhe_cpf["zona_eleitoral"],
        tit_eleit_municipio=detalhe_cpf["cidade_expedicao"]["nome"],
        tit_eleit_municipio_id=detalhe_cpf["cidade_expedicao"]["id_municipio_athenas"],
    )

    criar_escol_pessoa_fisica_convidado(
        pessoa_fisica_convidado,
        escolaridade=detalhe_cpf["id_escolaridade"],
        coeficiente_graduacao=detalhe_cpf["coeficiente_graduacao"],
        nome_instituicao_graduacao=detalhe_cpf["nome_instituicao_graduacao"],
        data_conclusao_graduacao=detalhe_cpf["data_conclusao_graduacao"],
        nome_instituicao_pos_graduacao=detalhe_cpf["nome_instituicao_pos_graduacao"],
    )

    criar_ender_pessoa_fisica_convidado(
        pessoa_fisica_convidado,
        tipo_endereco=detalhe_cpf["tipo_endereco"],
        tipo_logradouro=detalhe_cpf["tipo_logradouro"],
        logradouro=detalhe_cpf["logradouro"],
        numero=detalhe_cpf["numero"],
        compl=detalhe_cpf["complemento"],
        bairro=detalhe_cpf["bairro"],
        cep=detalhe_cpf["cep"],
        municipio_id=detalhe_cpf["municipio"]["id_municipio_athenas"],
    )

    criar_dados_bancarios_convidado(
        pessoa_fisica_convidado,
        banco=detalhe_cpf["banco"],
        tipo_conta=detalhe_cpf["tipo_conta"],
        numero_agencia=detalhe_cpf["numero_agencia"],
        numero_conta=detalhe_cpf["numero_conta"],
    )

    convite_nomeacao = criar_convite_nomeacao(
        pessoa_fisica_convidado,
        tipo_nomeacao=tipo_nomeacao,
        classificado=detalhe_cpf["classificado"],
        status_convocacao=detalhe_cpf["status_convocacao"],
        data_convocacao=detalhe_cpf["data_convocacao"],
        data_email_convocacao=detalhe_cpf["data_email_convocacao"],
        data_desistencia=detalhe_cpf["data_desistencia"],
        data_resposta=detalhe_cpf["data_resposta"],
        data_possivel_expericao=detalhe_cpf["data_possivel_expiracao"],
        data_expiracao=detalhe_cpf["data_expiracao"],
    )

    if len(detalhe_cpf["documentos"]) > 0:
        for anexo_form in detalhe_cpf["documentos"]:
            arquivo_relative_path = anexo_form["relative_path"]
            anexo_infos = criar_anexo_infos_convite(
                convite_nomeacao,
                tipo_documento=anexo_form["tipo_documento"]["id_documento_tipo"],
                tipo_documento_descr=anexo_form["tipo_documento"]["descricao"],
                arquivo_nome=anexo_form["documento"],
                arquivo_nome_original=anexo_form["nome_original"],
                api_relative_path=arquivo_relative_path,
                api_diretorio=anexo_form["tipo_documento"]["directory"],
            )

    cpf = normalizar_cpf(pessoa_fisica_convidado.documentacao.cpf)
    q_pf_athenas = PessoaFisica.objects.filter(cpf=cpf)
    if q_pf_athenas.exists():
        log.info(f">>> Atualizando cadastro do Athenas para: {pessoa_fisica_convidado}")
        pf_athenas = q_pf_athenas.first()
        atualizar_cadastro_pf_athenas(q_pf_athenas, pessoa_fisica_convidado)

        if (
            pessoa_fisica_convidado.documentacao.cnh_numero is not None
            and pf_athenas.cnh is not None
        ):
            apagar_cnh_pf_athenas(pf_athenas.cnh)
    else:
        log.info(f">>> Criando cadastro no Athenas para: {pessoa_fisica_convidado}")
        pf_athenas = criar_cadastro_pf_athenas(pessoa_fisica_convidado)

    if pessoa_fisica_convidado.documentacao.cnh_numero is not None:
        criar_cadastro_cnh_pf_athenas(pessoa_fisica_convidado.documentacao, pf_athenas)

    criar_endereco_athenas(pf_athenas, pessoa_fisica_convidado)
    criar_tel_athenas(pf_athenas, pessoa_fisica_convidado)

    if hasattr(pessoa_fisica_convidado, "dados_bancarios"):
        criar_dados_bancarios_athenas(pf_athenas, pessoa_fisica_convidado)


def apagar_registros_convite(convite):
    DadoBancarioConvidado.objects.filter(convidado=convite.convidado).delete()
    EnderecoConvidado.objects.filter(convidado=convite.convidado).delete()
    EscolaridadeConvidado.objects.filter(convidado=convite.convidado).delete()
    DocumentoConvidado.objects.filter(convidado=convite.convidado).delete()
    AnexoConvite.objects.filter(convite=convite).delete()
    ConviteNomeacao.objects.filter(pk=convite.pk).delete()
    PessoaFisicaConvidado.objects.filter(pk=convite.convidado.pk).delete()
