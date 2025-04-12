from dateutil.relativedelta import relativedelta

from contrib.daterange import NewDateRange


def preparar_res_detalhado(data, valor_diaria, ambito, base_calculo):
    """
    Método responsável em normalizar a resposta da informação detalhada do destino.
    """

    return {
        "data": data.strftime("%d/%m/%Y"),
        "valor_diaria": round(valor_diaria, 2),
        "valor_desc_trasporte": round((base_calculo["transporte"] / 30), 2),
        "valor_desc_alimentacao": round((base_calculo["alimentacao"] / 30), 2),
        "ambito": ambito,
    }


def buscar_destinos_detalhado(benef):
    """
    Método responsável por buscar as informações dos destinos e retornar de uma forma estrutura
    """

    if hasattr(benef, "calculos_diarias_consolidados") is False:
        return {}
    else:
        consolidado = benef.calculos_diarias_consolidados
        valor_base_desc_transp = consolidado.valor_base_desc_transporte
        valor_base_desc_alim = consolidado.valor_base_desc_alimentacao
        valor_base_diaria = consolidado.valor_base_diaria
        res = {
            "base_calculo": {
                "subsidio": (
                    "-"
                    if consolidado.valor_base_subsidio == 0
                    else consolidado.valor_base_subsidio
                ),
                "transporte": round(valor_base_desc_transp, 2),
                "alimentacao": round(valor_base_desc_alim, 2),
                "valor_diaria": round(valor_base_diaria, 2),
            },
            "consolidado": {
                "total_diarias": (
                    consolidado.qtd_total_diarias_deferido
                    if consolidado.qtd_total_diarias_deferido
                    else consolidado.qtd_total_diarias
                ),
                "valor_bruto": round(consolidado.valor_total_bruto, 2),
                "valor_total_desc_alimentacao": round(
                    consolidado.valor_desc_alimentacao, 2
                ),
                "valor_total_desc_transporte": round(
                    consolidado.valor_desc_transporte, 2
                ),
                "valor_liquido": round(consolidado.valor_total_liquido, 2),
                "valor_liquido_deferido": (
                    round(consolidado.valor_total_liquido_deferido, 2)
                    if consolidado.valor_total_liquido_deferido
                    else "-"
                ),
            },
            "excedente": {
                "qtd_total_diarias_calculadas": consolidado.qtd_total_diarias_calculadas,
                "qtd_total_diarias": consolidado.qtd_total_diarias,
                "qtd_total_excedente": consolidado.qtd_total_excedente,
            },
            # 'detalhado': [],
        }

        # destinos = benef.destinos.order_by('data')
        # for i_destinos,destino in enumerate(destinos):
        #     if(i_destinos == (len(destinos) - 1)):
        #         valor_diaria = (destino.valor_diaria * destino.qtd_diarias)
        #         res['detalhado'].append(preparar_res_detalhado(destino.data, valor_diaria, destino.get_tipo_display(), res['base_calculo']))
        #     else:
        #         data_prox_destino = destinos[i_destinos + 1].data - relativedelta(days=1)
        #         dt_range = NewDateRange(destino.data, data_prox_destino)
        #         for dt in dt_range.iter():
        #             res['detalhado'].append(preparar_res_detalhado(dt, destino.valor_diaria, destino.get_tipo_display(), res['base_calculo']))

        return res
