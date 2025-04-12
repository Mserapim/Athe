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
    FLUXO_PRESTACAO_CONTAS_ENTREGUE,
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


def importar_dados_sisdias():

    buscar_dados_api()


def buscar_dados_api():

    page = 1

    params = {
        "per_page": 100,
        "ano_inicial": 2025,
        "ano_final": 2025,
    }

    url = f"{SISDIAS_API_URL}v1/diarias/porAno"

    headers = {"Authorization": f"Bearer {SISDIAS_TOKEN}"}

    while True:
        params["page"] = page
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            dados = response.json()
            if dados["data"]:
                for diaria in dados["data"]:
                    importar_diaria(diaria)
                page += 1
            else:
                break
        else:
            log.error(f"Erro ao buscar diárias: {response.text}")
            break


def importar_diaria(diaria):

    try:
        servidor = Servidor.objects.get(matricula=diaria.get("chapa_servidor"))
        set_current_user(servidor.user.username)
    except:
        set_current_user("lsilvente")

    with transaction.atomic():
        viagem = criar_viagem(diaria)

        print(viagem)

        lista_externos = [
            0,
            "0",
            000000,
            "000000",
            90,
            "90",
            116,
            "116",
            123,
            "123",
            140,
            "140",
            156,
            "156",
            165,
            "165",
            193,
            "193",
        ]

        if diaria.get("chapa_servidor") in lista_externos or diaria.get(
            "sdia08_cdgpessoa_externa"
        ):
            beneficiario = criar_beneficiario_externo(diaria, viagem)
        else:
            beneficiario = criar_beneficiario_interno(diaria, viagem)

        if beneficiario is False:
            raise Exception("beneficiario não criado")

        try:
            criar_dados_bancarios(diaria, beneficiario)

            criar_evento_destinos(diaria, beneficiario)

            criar_calculo(diaria, beneficiario)

            criar_prestacao_contas(diaria, beneficiario)

            criar_pagamento(diaria, beneficiario)

            criar_historico(beneficiario)
        except Exception as e:
            log.info(f"erro na criação dos dados extras {e}")
            raise Exception(f"erro na criação dos dados extras {e}")


def buscar_datas(diaria):
    data_inicio = None
    data_fim = None
    if diaria.get("itens"):
        destinos = diaria.get("itens")
        destinos = sorted(
            destinos, key=lambda x: datetime.strptime(x["data"], "%Y-%m-%d %H:%M:%S")
        )

        if len(destinos) > 1:
            data_inicio = datetime.strptime(
                destinos[0]["data"], "%Y-%m-%d %H:%M:%S"
            ).date()
            data_fim = datetime.strptime(
                destinos[-1]["data"], "%Y-%m-%d %H:%M:%S"
            ).date()
        else:
            data_inicio = datetime.strptime(
                destinos[0]["data"], "%Y-%m-%d %H:%M:%S"
            ).date()
            data_fim = datetime.strptime(
                destinos[0]["data"], "%Y-%m-%d %H:%M:%S"
            ).date()

    return data_inicio, data_fim


def buscar_tipo_viagem(diaria):

    num_diaria_exterior = int(diaria.get("num_diaria_exterior", 0))
    num_diaria_pais = int(diaria.get("num_diaria_pais", 0))

    if num_diaria_exterior:
        return "INTERNACIONAL"
    if num_diaria_pais:
        return "NACIONAL"

    return "ESTADUAL"


def criar_viagem(diaria):
    data_inicio, data_fim = buscar_datas(diaria)
    data_viagem = datetime.strptime(diaria.get("data"), "%Y-%m-%d %H:%M:%S").date()

    try:
        motivo = Choice.objects.get(
            name="MOTIVO_VIAGEM", cvalue=diaria.get("tipo_origem")
        ).value
    except:
        motivo = None
    try:
        finalidade = Choice.objects.get(
            name="FINALIDADE_VIAGEM",
            cvalue=diaria.get("sdia12_cdgtipo_finalidade"),
        ).value
    except:
        finalidade = None

    try:
        servidor = Servidor.objects.get(matricula=diaria.get("chapa_servidor"))
        tipo_solicitante = buscar_tipo_solicitante_viagem(servidor)
    except:
        tipo_solicitante = None

    q_beneficiario = Beneficiario.objects.filter(codigo=diaria.get("numero"))

    if q_beneficiario.exists():
        viagem = q_beneficiario.first().viagem

        viagem.data_inicio_viagem = data_inicio or data_viagem
        viagem.data_fim_viagem = data_fim or data_viagem
        viagem.resumo = diaria.get("informacoes_adicionais", "")
        viagem.justificativa = diaria.get("finalidade", "")
        viagem.finalidade_viagem = finalidade
        viagem.tipo_viagem = buscar_tipo_viagem(diaria)
        viagem.motivo_viagem = motivo
        viagem.tipo_solicitante = tipo_solicitante
        viagem.gedoc_antigo = diaria.get("protocolo")
        viagem.gedoc_unico = diaria.get("numerounicocnmp")
        viagem.created_at = data_viagem

        viagem.save()
    else:
        viagem = Viagem.objects.create(
            importada=True,
            data_inicio_viagem=data_inicio or data_viagem,
            data_fim_viagem=data_fim or data_viagem,
            resumo=diaria.get("informacoes_adicionais", ""),
            justificativa=diaria.get("finalidade", ""),
            finalidade_viagem=finalidade,
            tipo_viagem=buscar_tipo_viagem(diaria),
            motivo_viagem=motivo,
            tipo_solicitante=tipo_solicitante,
            gedoc_antigo=diaria.get("protocolo"),
            gedoc_unico=diaria.get("numerounicocnmp"),
        )

        viagem.created_at = data_viagem

        viagem.save()

    return viagem


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

    pessoa_externa = diaria.get("pessoa_externa")

    if pessoa_externa is None:
        return False

    if pessoa_externa.get("cpf"):
        cpf = pessoa_externa.get("cpf").replace(".", "").replace("-", "")
        try:
            documents.CPF(cpf)
        except:
            log.info("cpf invalido")
            return False

        try:
            pessoa = PessoaFisica.objects.get(cpf=cpf)
        except:
            email = "" if "@mpmt" in diaria.get("email") else diaria.get("email")
            pessoa = PessoaFisica.objects.create(
                cpf=cpf,
                social_name=diaria.get("nome_servidor"),
                nome=diaria.get("nome_servidor"),
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

    if diaria.get("situacao") == 3:
        fluxo = FluxoViagem.objects.get(id=FLUXO_CANCELADO)
    elif verifica_relatorio_pendente(diaria):
        fluxo = FluxoViagem.objects.get(id=FLUXO_FINALIZADO)
    else:
        fluxo = FluxoViagem.objects.get(id=FLUXO_AGUARDADO_PRESTACAO_CONTAS)

    data_inicio, data_fim = buscar_datas(diaria)

    if data_inicio and data_inicio > datetime.now().date():
        fluxo = FluxoViagem.objects.get(id=FLUXO_PRESTACAO_CONTAS_ENTREGUE)

    beneficiario, _ = Beneficiario.objects.get_or_create(
        viagem=viagem,
        servidor=servidor,
        codigo=diaria.get("numero"),
        numero_empenho=diaria.get("empenho"),
    )

    if beneficiario.id in lista_cancelados:
        fluxo = FluxoViagem.objects.get(id=FLUXO_CANCELADO)

    beneficiario.fluxo = fluxo
    beneficiario.save()

    return beneficiario


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

    servidor = Servidor.objects.get(matricula=diaria.get("chapa_servidor"))
    if diaria.get("situacao") == 3:
        fluxo = FluxoViagem.objects.get(id=FLUXO_CANCELADO)
    elif verifica_relatorio_pendente(diaria):
        fluxo = FluxoViagem.objects.get(id=FLUXO_FINALIZADO)
    else:
        fluxo = FluxoViagem.objects.get(id=FLUXO_AGUARDADO_PRESTACAO_CONTAS)

    data_inicio, data_fim = buscar_datas(diaria)

    if data_inicio and data_inicio > datetime.now().date():
        fluxo = FluxoViagem.objects.get(id=FLUXO_PRESTACAO_CONTAS_ENTREGUE)

    beneficiario, _ = Beneficiario.objects.get_or_create(
        servidor=servidor, codigo=diaria.get("numero"), viagem=viagem
    )

    if beneficiario.id in lista_cancelados:
        fluxo = FluxoViagem.objects.get(id=FLUXO_CANCELADO)

    beneficiario.fluxo = fluxo
    beneficiario.numero_empenho = diaria.get("empenho")
    beneficiario.save()

    return beneficiario


def criar_evento_destinos(diaria, beneficiario):

    evento, _ = EventoBeneficiario.objects.get_or_create(
        titulo="importação",
        beneficiario=beneficiario,
        data_inicio=beneficiario.viagem.data_inicio_viagem,
        data_fim=beneficiario.viagem.data_fim_viagem,
    )

    trechos = diaria.get("itens", [])

    origem = buscar_localidade_athenas(
        diaria.get("origem").get("localidade"), diaria.get("origem").get("uf")
    )

    for trecho in trechos:
        trecho_athenas = buscar_localidade_athenas(
            trecho.get("localidade").get("localidade"),
            trecho.get("localidade").get("uf"),
        )
        if trecho_athenas:
            data = datetime.strptime(trecho.get("data"), "%Y-%m-%d %H:%M:%S")
            destino, _ = Destino.objects.get_or_create(
                beneficiario=beneficiario,
                municipio_origem=origem,
                municipio_destino=trecho_athenas,
                data=data,
                forma_deslocamento=meio_para_tipo_deslocamento(diaria.get("meio")),
            )

            if not destino in evento.destinos.all():
                evento.destinos.add(destino)


def criar_calculo(diaria, beneficiario):
    calculo, _ = CalculoConsolidado.objects.get_or_create(beneficiario=beneficiario)

    calculo.qtd_total_diarias_calculadas = total_diarias(diaria)
    calculo.qtd_total_diarias = total_diarias(diaria)
    calculo.qtd_total_excedente = 0
    calculo.qtd_total_diarias_deferido = total_diarias(diaria)
    calculo.qtd_total_diarias_dentro_uf = diaria.get("num_diaria_estado", 0)
    calculo.qtd_total_diarias_fora_uf = total_diarias_fora_mt(diaria)
    calculo.valor_base_diaria = get_valor_decimal(0)  # Ver como preencher
    calculo.valor_base_subsidio = get_valor_decimal(
        diaria.get("subsidio", 0)
    )  # Ver como preencher
    calculo.valor_base_desc_transporte = get_valor_decimal(
        diaria.get("valor_uni_transportes", 0)
    )
    calculo.valor_desc_transporte = get_valor_decimal(
        diaria.get("valor_transportes", 0)
    )
    calculo.valor_base_desc_alimentacao = get_valor_decimal(
        diaria.get("valor_uni_auxilios", 0)
    )
    if int(diaria.get("qtd_auxilios", 0) or 0) and Decimal(
        diaria.get("valor_uni_auxilios", 0) or 0
    ):
        calculo.valor_desc_alimentacao = get_valor_decimal(
            (diaria.get("qtd_auxilios", 0)) * (diaria.get("valor_uni_auxilios", 0))
        )
    else:
        calculo.valor_desc_alimentacao = get_valor_decimal(0)

    calculo.valor_total_diarias_dentro_estado = get_valor_decimal(
        diaria.get("valor_unit_estado", 0)
    )
    calculo.valor_total_diarias_fora_estado = get_valor_decimal(
        diaria.get("valor_unit_pais", 0)
    )  # Ver como preencher validar
    calculo.valor_total_veiculo_mp = get_valor_decimal(0)  # Ver como preencher
    calculo.valor_total_desconto = get_valor_decimal(diaria.get("totaldescontos", 0))
    calculo.valor_total_bruto = get_valor_decimal(diaria.get("valor_total_bruto", 0))
    calculo.valor_total_liquido = get_valor_decimal(
        diaria.get("valor_total_liquido", 0)
    )
    calculo.valor_total_liquido_deferido = get_valor_decimal(
        diaria.get("valor_total_liquido", 0)
    )
    calculo.reanalise = False

    calculo.save()


def criar_prestacao_contas(diaria, beneficiario):

    data_entrega = None
    if diaria.get("data_relatorio"):
        data_entrega = datetime.strptime(
            diaria.get("data_relatorio"), "%Y-%m-%d %H:%M:%S"
        ).date()

    if verifica_relatorio_pendente(diaria):
        status = "aprovado"
    else:
        status = "aguardando"

    if data_entrega is None or data_entrega > datetime.now().date():
        status = "entregue"

    prestacao, _ = PrestacaoContas.objects.get_or_create(
        beneficiario=beneficiario,
    )

    prestacao.status = status
    prestacao.obs_resultado = diaria.get("descricao_resultado")
    prestacao.obs = diaria.get("observacoes")
    prestacao.data_entrega = data_entrega
    prestacao.viagem_realizada = True if diaria.get("viagemefetivada") == "S" else False

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


def criar_pagamento(diaria, beneficiario):

    data_pagamento = None
    if diaria.get("data_pagamento"):
        data_pagamento = datetime.strptime(
            diaria.get("data_pagamento"), "%Y-%m-%d %H:%M:%S"
        ).date()

    pagamento = None
    if data_pagamento:
        pagamento, criado = Pagamento.objects.get_or_create(
            beneficiario=beneficiario, status="pago", data_pgto=data_pagamento
        )


def verificar_arquivos_sdias(diaria):
    url = f"{SISDIAS_API_URL}v1/diarias/arquivos"

    headers = {"Authorization": f"Bearer {SISDIAS_TOKEN}"}
    params = {"diaria": diaria.get("numero")}

    try:
        response = requests.get(url, params=params, headers=headers)

        resposta = response.json()

        return resposta.get("relatorio", False), resposta.get("comprovante", False)
    except:
        return False, False


def importar_arquivos_sdias(diaria, tipo):

    n_os = diaria.get("numero")

    url = f"https://painel-diarias.mpmt.mp.br/api/v1/diarias/arquivos/serveFile"

    headers = {
        "Authorization": "Bearer T0ZOM-W6oc3EnzQHEwu79Tt_yUl9Jqg9BOUA8XvREIhQ2Rr3hmWTWGEl0whb4iGuWiHqirjOZeHWWpiBZ_DqPtYG_4yxR1WHaFhPZAe_z87PQvBptsutUg6fEuddjlJo"
    }
    params = {"diaria": n_os, "tipo_arquivo": tipo}

    response = requests.get(url, headers=headers, params=params, stream=True)

    filename = None

    if (
        tipo == "relatorio"
        and diaria.get("relatorio_viagem_arquivo")
        and diaria.get("relatorio_viagem_arquivo") != ""
    ):
        filename = diaria.get("relatorio_viagem_arquivo")

    if (
        tipo == "comprovante"
        and diaria.get("comprovante_arquivo")
        and diaria.get("comprovante_arquivo") != ""
    ):
        filename = diaria.get("comprovante_arquivo")

    if filename is None:
        filename = f"{tipo}-{n_os}-.pdf"

    user = get_current_user()

    arquivo = UploadFile.upload_steam(
        data=response.content, filename=filename, user=user
    )

    return arquivo


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


def criar_dados_bancarios(diaria, beneficiario):

    dados_bancarios, _ = DadosBancariosImportacao.objects.get_or_create(
        beneficiario=beneficiario,
    )
    dados_bancarios.banco = diaria.get("banco", "") or ""
    dados_bancarios.agencia = diaria.get("agencia", "") or ""
    dados_bancarios.conta = diaria.get("conta", "") or ""
    dados_bancarios.save()


def verifica_relatorio_pendente(diaria):
    data_viagem = datetime.strptime(diaria.get("data"), "%Y-%m-%d %H:%M:%S").date()

    if (
        data_viagem < datetime(2024, 1, 1).date()
        or data_viagem > datetime(2025, 1, 1).date()
    ):
        return True

    if diaria.get("relatorio_entregue") in [1, 2, 3, 4, None]:
        return True

    if diaria.get("descricao_resultado"):
        return True

    return False


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


def get_valor_decimal(valor):
    if valor is None or valor == "":
        valor = 0
    return Decimal(valor)


def total_diarias(diaria):
    diarias_mt = get_valor_decimal(diaria.get("num_diaria_estado", 0))
    diarias_fora_mt = total_diarias_fora_mt(diaria)
    return diarias_mt + diarias_fora_mt


def total_diarias_fora_mt(diaria):
    diarias_pais = get_valor_decimal(diaria.get("num_diaria_pais", 0))
    diarias_exterior = get_valor_decimal(diaria.get("num_diaria_exterior", 0))
    return diarias_pais + diarias_exterior


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


def importar_dados_sevidor(diaria):
    try:
        servidor = Servidor.objects.get(matricula=diaria.get("chapa_servidor"))
        set_current_user(servidor.user.username)
    except:
        set_current_user("lsilvente")

    with transaction.atomic():
        viagem = criar_viagem(diaria)

        print(viagem)

        lista_externos = [
            0,
            "0",
            000000,
            "000000",
            90,
            "90",
            116,
            "116",
            123,
            "123",
            140,
            "140",
            156,
            "156",
            165,
            "165",
            193,
            "193",
        ]

        if diaria.get("chapa_servidor") in lista_externos or diaria.get(
            "sdia08_cdgpessoa_externa"
        ):
            beneficiario = criar_beneficiario_externo(diaria, viagem)
        else:
            beneficiario = criar_beneficiario_interno(diaria, viagem)

        if beneficiario is False:
            raise Exception("beneficiario não criado")

        try:
            criar_dados_bancarios(diaria, beneficiario)

            criar_evento_destinos(diaria, beneficiario)

            criar_calculo(diaria, beneficiario)

            criar_prestacao_contas(diaria, beneficiario)

            criar_pagamento(diaria, beneficiario)

            criar_historico(beneficiario)
        except Exception as e:
            log.info(f"erro na criação dos dados extras {e}")
            raise Exception(f"erro na criação dos dados extras {e}")


def importar_diarias_api(params, user):

    set_current_user(user)

    relatorio = {}

    url = f"{SISDIAS_API_URL}v1/diarias/porAno"

    headers = {"Authorization": f"Bearer {SISDIAS_TOKEN}"}

    qtd_total = 0
    qtd_sucesso = 0
    qtd_falha = 0

    params["per_page"] = 1000

    page = 1
    log.info("iniciando a importacao")
    while True:
        params["page"] = page
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            dados = response.json()
            if dados["data"]:
                qtd_total = qtd_total + len(dados["data"])
                for diaria in dados["data"]:
                    try:
                        log.info(f'Importando a os : {diaria.get("numero")}')
                        importar_diaria(diaria)
                        relatorio[diaria.get("numero")] = "SUCESSO"
                        qtd_sucesso += 1
                    except Exception as e:
                        import traceback

                        error_message = traceback.format_exc()
                        relatorio[diaria.get("numero")] = error_message
                        qtd_falha += 1
                        log.error(error_message)
                page += 1
                log.info("page: ", page)
            else:
                break
        else:
            log.info(response)
            log.error(f"Erro: {response.text}")
            log.info("page2: ", page)

            break

    notificar_administradores_solicitante(relatorio, qtd_total, qtd_sucesso, qtd_falha)
