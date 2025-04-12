from decimal import Decimal
from diarias.models import (
    Beneficiario,
    CalculoConsolidado,
    CargoDiarias,
    DadosBancariosImportacao,
    Destino,
    EventoBeneficiario,
    FluxoViagem,
    HistoricoFluxoViagemBeneficiario,
    Pagamento,
    PrestacaoContas,
    PrestacaoContasAnexo,
    Viagem,
    GrupoAprovador,
)

from rh.models import Servidor, Localidade, Estado, PessoaFisica, Pais
from rh.sisdias.models import (
    Sdia01OrdemServico,
    Sdia09CargoPessExt,
    Sdia02Localidade,
    Sdia08PessoaExterna,
)
from contrib.middleware import set_current_user, get_current_user
from django.db import transaction
from django.db import connections
from standard.models import Choice
from diarias.const import (
    FLUXO_FINALIZADO,
    FLUXO_CANCELADO,
    FLUXO_AGUARDADO_PRESTACAO_CONTAS,
)
from contrib import documents

from contrib.utils import getLogger
from diarias.utils.utils import buscar_tipo_solicitante_viagem, criar_historico
from datetime import datetime
from contrib.uploadfile import UploadFile
import requests
from common.util.send_email import EmailNotification
from django.template.loader import render_to_string
from app.settings import SISDIAS_API_URL, SISDIAS_TOKEN

log = getLogger(__name__)


def dict_cursor(cursor):
    """Converte o resultado do cursor em um dicionário."""
    columns = [col[0].lower() for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor]


def notificar_administradores_solicitante(relatorio, qtd_total, qtd_sucesso, qtd_falha):
    message = f"""
    <h1>Relatório de Importação</h1>
    <p>Foram encontradas <strong>{qtd_total}</strong> diárias: <strong>{qtd_sucesso}</strong> foram importadas com sucesso e <strong>{qtd_falha}</strong> apresentaram falhas.</p>
    """

    dados = ""

    for item, valor in relatorio.items():
        dados += f"""
            <tr class="custom-row">
                <td class="custom-cell" >{ item }</td>
                <td class="custom-cell" >{ valor }</td>
            </tr>
        """

    message += f"""
        <table class="custom-table">
            <tbody>
                <tr>
                    <th class="custom-header"><strong>Número OS</strong></th>
                    <th class="custom-header"><strong>Status/Erro</strong></th>
                </tr>
                {dados}
            </tbody>
        </table>
    """

    user = get_current_user()
    lista_adm = GrupoAprovador.objects.get(id=14).servidores.all()

    destinatarios = [
        {
            "nome": f"{user.servidor.pessoa_fisica.social_name}",
            "email": f"{user.servidor.pessoa_fisica.email_institucional if user.servidor.pessoa_fisica.email_institucional else user.servidor.pessoa_fisica.email_pessoal}",
        },
    ]

    for adm in lista_adm:
        destinatarios.append(
            {
                "nome": f"{adm.pessoa_fisica.social_name}",
                "email": f"{adm.pessoa_fisica.email_institucional if adm.pessoa_fisica.email_institucional else adm.pessoa_fisica.email_pessoal}",
            }
        )

    html_content = render_to_string("util/template_email.html", {"message": message})
    response = EmailNotification().send_email_default(
        destinatarios, "Importação Diárias", html_content
    )


def importar_diarias_api(lista_os, user):

    set_current_user(user)

    relatorio = {}
    qtd_total = lista_os.count()
    qtd_sucesso = 0
    qtd_falha = 0
    log.info("iniciando a importacao")
    for n_os in lista_os:
        try:
            log.info(f"Importando a os : {n_os.numero}")
            importar_dados_sevidor(n_os)
            relatorio[n_os.numero] = "SUCESSO"
            qtd_sucesso += 1
        except Exception as e:
            import traceback

            error_message = traceback.format_exc()
            relatorio[n_os.numero] = error_message
            qtd_falha += 1
            log.error(error_message)

    notificar_administradores_solicitante(relatorio, qtd_total, qtd_sucesso, qtd_falha)


def importar_dados():

    # importar todos os cargos usados nos colaboradores externos
    set_current_user("athenas_diarias")
    importar_cargos_diarias()
    criar_choices()

    lista_os = Sdia01OrdemServico.objects.using("sisdias").all().order_by("-numero")

    inicio = datetime.now()

    qtd_total = lista_os.count()
    qtd_passou = 0
    qtd_erros = 0
    log.info("iniciando a importacao")
    for n_os in lista_os:
        try:
            log.info(f"Importando a os : {n_os.numero}")
            importar_dados_sevidor(n_os)
            qtd_passou += 1
        except Exception as e:
            qtd_erros += 1
            log.info(f"erro - {e}")

    log.info(f"Total - {qtd_total}")
    log.info(f"Total Passou - {qtd_passou}")
    log.info(f"Total erros - {qtd_erros}")

    log.info(f"Iniciou - {inicio}")
    log.info(f"Finalizou - {datetime.now()}")


def importar_dados_sevidor(sdia_os):
    try:
        servidor = Servidor.objects.get(matricula=sdia_os.chapa_servidor)
        set_current_user(servidor.user.username)
    except:
        set_current_user("lsilvente")

    with transaction.atomic():

        viagem = criar_viagem(sdia_os)

        lista_externos = [
            0,
            165,
            140,
            000000,
            "000000",
            "116",
            "193",
            "156",
            "123",
            "90",
            "0",
            "165",
            "140",
        ]

        if sdia_os.chapa_servidor in lista_externos:
            beneficiario = criar_beneficiario_externo(sdia_os, viagem)
        else:
            beneficiario = criar_beneficiario_interno(sdia_os, viagem)

        if beneficiario is False:
            raise Exception("beneficiario não criado")
            # return False

        try:
            criar_dados_bancarios(sdia_os, beneficiario)

            criar_evento_destinos(sdia_os, beneficiario)

            criar_calculo(sdia_os, beneficiario)

            criar_prestacao_contas(sdia_os, beneficiario)

            criar_pagamento(sdia_os, beneficiario)

            criar_historico(beneficiario)
        except Exception as e:
            log.info(f"erro na criação dos dados extras {e}")
            raise Exception(f"erro na criação dos dados extras {e}")


def get_valor_decimal(valor):
    if valor is None or valor == "":
        valor = 0
    return Decimal(valor)


def total_diarias(diaria):
    diarias_mt = diaria.num_diaria_estado
    diarias_fora_mt = total_diarias_fora_mt(diaria)
    return diarias_mt + diarias_fora_mt


def total_diarias_fora_mt(diaria):
    diarias_pais = diaria.num_diaria_pais
    diarias_exterior = diaria.num_diaria_exterior
    return diarias_pais + diarias_exterior


def importar_cargos_diarias():
    sisdia_cargos = Sdia09CargoPessExt.objects.using("sisdias").all()
    for cargo in sisdia_cargos:
        log.info(f"cadastrando o cargo {cargo.nomecargo}")
        novo_cargo, _ = CargoDiarias.objects.get_or_create(nome=cargo.nomecargo)


def buscar_cargo(nome):
    cargo, _ = CargoDiarias.objects.get_or_create()
    return cargo


def usuario_sacs(id):
    with connections["sacs"].cursor() as cursor:
        cursor.execute("""SELECT *FROM SACS.SACS01_USUARIO""")
        resultado = cursor.fetchall()

        if len(resultado) > 0:
            return resultado[0][1]

    return None


def buscar_tipo_viagem(diaria):

    if diaria.num_diaria_exterior:
        return "INTERNACIONAL"
    if diaria.num_diaria_pais:
        return "NACIONAL"

    return "ESTADUAL"


def buscar_datas(diaria):

    data_inicio = None
    data_fim = None

    with connections["sisdias"].cursor() as cursor:
        cursor.execute(
            f"""SELECT *FROM sdia04_os_localidade WHERE sdia01_numero_os={diaria.numero} order by DATA"""
        )
        resultado = cursor.fetchall()

    if len(resultado) > 0:
        if len(resultado) == 1:
            data_inicio = (resultado[0][3]).date()
            data_fim = (resultado[0][3]).date()
        else:
            data_inicio = (resultado[0][3]).date()
            data_fim = (resultado[-1][3]).date()
    return data_inicio, data_fim


def buscar_trechos(diaria):

    origem = buscar_localidade_athenas(
        diaria.sdia02_cdglocalidade_origem.localidade,
        diaria.sdia02_cdglocalidade_origem.uf,
    )

    with connections["sisdias"].cursor() as cursor:
        cursor.execute(
            f"""SELECT *FROM sdia04_os_localidade WHERE sdia01_numero_os={diaria.numero} order by DATA"""
        )
        resultado = dict_cursor(cursor)

    trechos = []

    for trecho in resultado:
        localidade = buscar_localidade_sisdias(trecho.get("sdia02_cdglocalidade"))
        os_localidade = buscar_localidade_athenas(
            localidade.get("localidade"), localidade.get("uf")
        )

        trechos.append(
            {
                "origem": origem,
                "destino": os_localidade,
                "data": trecho.get("data").date(),
            }
        )

    return trechos


def buscar_localidade_athenas(nome_localidade, uf):

    dic_correcao_nomes_athenas = {
        "Poxoréu": "POXOREO",
        "SÃO LUIZ": "SAO LUIS",
        "Santa Catarina": "Florianópolis",
    }

    nome_localidade = nome_localidade.lstrip().rstrip().replace("'", "")

    local = Localidade.objects.filter(
        nome__unaccent__icontains=nome_localidade, estado__sigla=uf
    )
    if local.exists():
        return local.last()
    else:

        nome_correto = dic_correcao_nomes_athenas.get(nome_localidade)
        if nome_correto:

            local = Localidade.objects.filter(
                nome__unaccent__icontains=nome_correto, estado__sigla=uf
            )
            if local.exists():
                return local.last()

        return criar_localidades_athenas(nome_localidade, uf)

    return None


def buscar_localidade_sisdias(id):
    with connections["sisdias"].cursor() as cursor:
        cursor.execute(f"""SELECT * FROM sdia02_localidade WHERE cdglocalidade={id}""")
        resultado = dict_cursor(cursor)

    if len(resultado) > 0:
        return resultado[0]

    return None


def buscar_qtd_trechos_localidades(diaria):
    with connections["sisdias"].cursor() as cursor:
        cursor.execute(
            f"""SELECT sdia02_cdglocalidade as localidade, count(*) as qtd FROM sdia04_os_localidade WHERE sdia01_numero_os={diaria.numero} GROUP BY sdia02_cdglocalidade """
        )
        resultado = dict_cursor(cursor)
    return resultado


def meio_para_tipo_deslocamento(meio):
    de_para = {
        0: "3",
        1: "4",
        2: "1",
        3: "0",
        4: "5",
        5: "6",
        6: "7",
        7: "",
        8: "0",
        9: "9",
        None: "",
    }

    return de_para.get(meio, "")


def criar_historico(beneficiario):

    hist_viagem = HistoricoFluxoViagemBeneficiario.objects.create(
        viagem=beneficiario.viagem,
        fluxo=beneficiario.fluxo,
        obs="Importação",
        decisao="importacao",
        tipo="viagem",
    )

    hist_beneficiario = HistoricoFluxoViagemBeneficiario.objects.create(
        viagem=beneficiario.viagem,
        beneficiario=beneficiario,
        fluxo=beneficiario.fluxo,
        obs="Importação",
        decisao="importacao",
        tipo="beneficiario",
    )


def criar_calculo(diaria, beneficiario):
    calculo, _ = CalculoConsolidado.objects.get_or_create(beneficiario=beneficiario)

    calculo.qtd_total_diarias_calculadas = total_diarias(diaria)
    calculo.qtd_total_diarias = total_diarias(diaria)
    calculo.qtd_total_excedente = 0
    calculo.qtd_total_diarias_deferido = total_diarias(diaria)
    calculo.qtd_total_diarias_dentro_uf = diaria.num_diaria_estado
    calculo.qtd_total_diarias_fora_uf = total_diarias_fora_mt(diaria)
    calculo.valor_base_diaria = get_valor_decimal(0)  # Ver como preencher
    calculo.valor_base_subsidio = get_valor_decimal(
        diaria.subsidio
    )  # Ver como preencher
    calculo.valor_base_desc_transporte = get_valor_decimal(diaria.valor_uni_transportes)
    calculo.valor_desc_transporte = get_valor_decimal(diaria.valor_transportes)
    calculo.valor_base_desc_alimentacao = get_valor_decimal(diaria.valor_uni_auxilios)
    calculo.valor_desc_alimentacao = get_valor_decimal(
        (diaria.qtd_auxilios or 0) * (diaria.valor_uni_auxilios or 0)
    )
    calculo.valor_total_diarias_dentro_estado = get_valor_decimal(
        diaria.valor_unit_estado
    )
    calculo.valor_total_diarias_fora_estado = get_valor_decimal(
        diaria.valor_unit_pais
    )  # Ver como preencher validar
    calculo.valor_total_veiculo_mp = get_valor_decimal(0)  # Ver como preencher
    calculo.valor_total_desconto = get_valor_decimal(diaria.totaldescontos)
    calculo.valor_total_bruto = get_valor_decimal(diaria.valor_total_bruto)
    calculo.valor_total_liquido = get_valor_decimal(diaria.valor_total_liquido)
    calculo.valor_total_liquido_deferido = get_valor_decimal(diaria.valor_total_liquido)
    calculo.reanalise = False

    calculo.save()


def criar_evento_destinos(diaria, beneficiario):

    evento, _ = EventoBeneficiario.objects.get_or_create(
        titulo="importação",
        beneficiario=beneficiario,
        data_inicio=beneficiario.viagem.data_inicio_viagem,
        data_fim=beneficiario.viagem.data_fim_viagem,
    )

    trechos = buscar_trechos(diaria)

    for trecho in trechos:
        destino, _ = Destino.objects.get_or_create(
            beneficiario=beneficiario,
            municipio_origem=trecho.get("origem"),
            municipio_destino=trecho.get("destino"),
            data=trecho.get("data"),
            forma_deslocamento=meio_para_tipo_deslocamento(diaria.meio),
        )

        if not destino in evento.destinos.all():
            evento.destinos.add(destino)


def criar_dados_bancarios(diaria, beneficiario):

    dados_bancarios, _ = DadosBancariosImportacao.objects.get_or_create(
        beneficiario=beneficiario,
        banco=diaria.banco or "",
        agencia=diaria.agencia or "",
        conta=diaria.conta or "",
    )


def criar_viagem(diaria):
    data_inicio, data_fim = buscar_datas(diaria)

    try:
        motivo = Choice.objects.get(
            name="MOTIVO_VIAGEM", cvalue=diaria.tipo_origem
        ).value
    except:
        motivo = None
    try:
        finalidade = Choice.objects.get(
            name="FINALIDADE_VIAGEM",
            cvalue=diaria.sdia12_cdgtipo_finalidade.cdgtipo_finalidade,
        ).value
    except:
        finalidade = None

    try:
        servidor = Servidor.objects.get(matricula=diaria.chapa_servidor)

        tipo_solicitante = buscar_tipo_solicitante_viagem(servidor)
    except:
        tipo_solicitante = None

    q_beneficiario = Beneficiario.objects.filter(codigo=diaria.numero)

    if q_beneficiario.exists():
        viagem = q_beneficiario.first().viagem

        viagem.data_inicio_viagem = data_inicio or diaria.data.date()
        viagem.data_fim_viagem = data_fim or diaria.data.date()
        viagem.resumo = diaria.informacoes_adicionais
        viagem.justificativa = diaria.finalidade
        viagem.finalidade_viagem = finalidade
        viagem.tipo_viagem = buscar_tipo_viagem(diaria)
        viagem.motivo_viagem = motivo
        viagem.tipo_solicitante = tipo_solicitante
        viagem.gedoc_antigo = diaria.protocolo
        viagem.gedoc_unico = diaria.numerounicocnmp
        viagem.created_at = diaria.data

        viagem.save()

    else:

        viagem = Viagem.objects.create(
            importada=True,
            data_inicio_viagem=data_inicio or diaria.data.date(),
            data_fim_viagem=data_fim or diaria.data.date(),
            resumo=diaria.informacoes_adicionais,
            justificativa=diaria.finalidade,
            finalidade_viagem=finalidade,
            tipo_viagem=buscar_tipo_viagem(diaria),
            motivo_viagem=motivo,
            tipo_solicitante=tipo_solicitante,
            gedoc_antigo=diaria.protocolo,
            gedoc_unico=diaria.numerounicocnmp,
        )

        viagem.created_at = diaria.data

        viagem.save()

    return viagem


def criar_beneficiario_interno(diaria, viagem):

    lista_cancelados = [
        53,
        2378,
        342,
        344,
        996,
        455,
        2285,
        831,
        1539,
        1801,
        2028,
        2036,
        2383,
        2437,
        2509,
        2577,
        2578,
        2579,
        2641,
        2684,
    ]

    servidor = Servidor.objects.get(matricula=diaria.chapa_servidor)
    if diaria.situacao == 3:
        fluxo = FluxoViagem.objects.get(id=FLUXO_CANCELADO)
    elif verifica_relatorio_pendente(diaria):
        fluxo = FluxoViagem.objects.get(id=FLUXO_FINALIZADO)
    else:
        fluxo = FluxoViagem.objects.get(id=FLUXO_AGUARDADO_PRESTACAO_CONTAS)

    beneficiario, _ = Beneficiario.objects.get_or_create(
        servidor=servidor, codigo=diaria.numero, viagem=viagem
    )

    if beneficiario.id in lista_cancelados:
        fluxo = FluxoViagem.objects.get(id=FLUXO_CANCELADO)

    beneficiario.fluxo = fluxo
    beneficiario.numero_empenho = diaria.empenho
    beneficiario.save()

    return beneficiario


def criar_beneficiario_externo(diaria, viagem):

    lista_cancelados = [
        53,
        2378,
        342,
        344,
        996,
        455,
        2285,
        831,
        1539,
        1801,
        2028,
        2036,
        2383,
        2437,
        2509,
        2577,
        2578,
        2579,
        2641,
        2684,
    ]

    try:
        if diaria.sdia08_cdgpessoa_externa is not None:
            pessoa_externa = diaria.sdia08_cdgpessoa_externa
        else:
            pessoa_externa = Sdia08PessoaExterna.objects.using("sisdias").get(
                nome=diaria.nome_servidor
            )
    except:
        log.info("os sem dados da pessoa externa")
        return False

    if pessoa_externa.cpf:
        cpf = pessoa_externa.cpf.replace(".", "").replace("-", "")
        try:
            documents.CPF(cpf)
        except:
            log.info("cpf invalido")
            return False

        try:
            pessoa = PessoaFisica.objects.get(cpf=cpf)
        except:
            email = "" if "@mpmt" in diaria.email else diaria.email
            pessoa = PessoaFisica.objects.create(
                cpf=cpf,
                social_name=diaria.nome_servidor,
                nome=diaria.nome_servidor,
                email_pessoal=email,
                sexo="N",
                municipio_naturalidade=Localidade.objects.get(pk=12360),
            )

    else:
        log.info("pessoa externa sem cpf, não pode cadastrar")
        return False

    servidor, _ = Servidor.objects.get_or_create(
        pessoa_fisica=pessoa, type_by_possession="COE", ativo=True
    )

    if diaria.situacao == 3:
        fluxo = FluxoViagem.objects.get(id=FLUXO_CANCELADO)
    elif verifica_relatorio_pendente(diaria):
        fluxo = FluxoViagem.objects.get(id=FLUXO_FINALIZADO)
    else:
        fluxo = FluxoViagem.objects.get(id=FLUXO_AGUARDADO_PRESTACAO_CONTAS)

    beneficiario, _ = Beneficiario.objects.get_or_create(
        viagem=viagem,
        servidor=servidor,
        codigo=diaria.numero,
        numero_empenho=diaria.empenho,
    )

    if beneficiario.id in lista_cancelados:
        fluxo = FluxoViagem.objects.get(id=FLUXO_CANCELADO)

    beneficiario.fluxo = fluxo
    beneficiario.save()

    return beneficiario


def criar_pagamento(diaria, beneficiario):

    pagamento = None
    if diaria.data_pagamento:
        pagamento, criado = Pagamento.objects.get_or_create(
            beneficiario=beneficiario,
            status="pago",
            data_pgto=diaria.data_pagamento.date(),
        )


def criar_prestacao_contas(diaria, beneficiario):

    if verifica_relatorio_pendente(diaria):
        status = "aprovado"
    else:
        status = "aguardando"

    prestacao, _ = PrestacaoContas.objects.get_or_create(
        beneficiario=beneficiario,
    )

    prestacao.status = status
    prestacao.obs_resultado = diaria.descricao_resultado
    prestacao.obs = diaria.observacoes
    prestacao.data_entrega = diaria.data_relatorio
    prestacao.viagem_realizada = True if diaria.viagemefetivada == "S" else False

    prestacao.save()

    relatorio, comprovante = verificar_arquivos_sdias(diaria)

    anexos = []

    if relatorio:
        arquivo = importar_arquivos_sdias(diaria, "relatorio")
        if arquivo:
            anexos.append(arquivo)

    if comprovante:
        arquivo = importar_arquivos_sdias(diaria, "comprovante")
        if arquivo:
            anexos.append(arquivo)

    for anexo in anexos:
        anexo_p, _ = PrestacaoContasAnexo.objects.get_or_create(
            prestacao=prestacao, arquivo=anexo
        )


def verificar_arquivos_sdias(diaria):
    url = f"{SISDIAS_API_URL}v1/diarias/arquivos?diaria={diaria.numero}"

    headers = {"Authorization": f"Bearer {SISDIAS_TOKEN}"}

    try:
        response = requests.get(url, headers=headers)

        resposta = response.json()

        return resposta.get("relatorio", False), resposta.get("comprovante", False)
    except:
        return False, False


def importar_arquivos_sdias(diaria, tipo):

    n_os = diaria.numero

    url = f"https://painel-diarias.mpmt.mp.br/api/v1/diarias/arquivos/serveFile?diaria={n_os}&tipo_arquivo={tipo}"

    headers = {
        "Authorization": "Bearer T0ZOM-W6oc3EnzQHEwu79Tt_yUl9Jqg9BOUA8XvREIhQ2Rr3hmWTWGEl0whb4iGuWiHqirjOZeHWWpiBZ_DqPtYG_4yxR1WHaFhPZAe_z87PQvBptsutUg6fEuddjlJo"
    }

    response = requests.get(url, headers=headers, stream=True)

    filename = None

    if (
        tipo == "relatorio"
        and diaria.relatorio_viagem_arquivo
        and diaria.relatorio_viagem_arquivo != ""
    ):
        filename = diaria.relatorio_viagem_arquivo

    if (
        tipo == "comprovante"
        and diaria.comprovante_arquivo
        and diaria.comprovante_arquivo != ""
    ):
        filename = diaria.comprovante_arquivo

    if filename is None:
        filename = f"{tipo}-{n_os}-.pdf"

    user = get_current_user()

    arquivo = UploadFile.upload_steam(
        data=response.content, filename=filename, user=user
    )

    return arquivo


def criar_choices():
    Choice.objects.get_or_create(
        name="FINALIDADE_VIAGEM",
        value="80",
        cvalue="76",
    )


def criar_localidades_athenas(nome_localidade, uf):

    try:
        estado = Estado.objects.get(sigla=uf)
        set_current_user("athenas")
        localidade, _ = Localidade.objects.get_or_create(
            nome=nome_localidade, estado=estado
        )

        return localidade
    except:

        if uf == "IN":

            dic_nome_pais = {
                "Estados Unidos da América": "ESTADOS UNIDOS",
                "Lisboa": "PORTUGAL",
                "Coimbra": "PORTUGAL",
            }

            nome_pais = dic_nome_pais.get(nome_localidade, nome_localidade)

            pais = Pais.objects.filter(nome__unaccent__icontains=nome_pais).first()
            estado, _ = Estado.objects.get_or_create(
                pais=pais, nome__unaccent__icontains=nome_localidade
            )

            localidade, _ = Localidade.objects.get_or_create(
                nome__unaccent__icontains=nome_localidade, estado=estado
            )

            return localidade

        log.info("estado invalido")
        return None


def verifica_relatorio_pendente(diaria):

    if diaria.data < datetime(2024, 1, 1):
        return True

    if diaria.relatorio_entregue in [1, 2, 3, 4, None]:
        return True

    if diaria.descricao_resultado and diaria.descricao_resultado != "":
        return True

    return False
