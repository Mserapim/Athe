import {ListPayload} from "../@base/list-payload";
import {ListPaginated} from "../@base/list-paginated";
import {useGet} from "../@base/use-get";

interface Payload extends ListPayload {
    keyword?: string;
}

class ResponseItem {
    id: number;
    ambiente: number;
    ambiente_display: string;
    layout_versao: string;
    webservice_envio: string;
    webservice_consulta: string;
    inicio_vigencia: string;
    fim_vigencia: string;
    data_corte_s2231: string;
    orgao_empregador_id: number;
    orgao_empregador_display: string;
    tabela_iniciais: string;
    nao_periodicos: string;
    periodicos: string;
    sst: string;
    envio_fila: boolean;
    criado_em: string;
    modificado_em: string;
    criado_por: string;
    modificado_por: string;
    responsavel_id: number;
    responsavel: string;
    responsavel_sowfware_house_id: number;
    responsavel_sowfware_house: string;
    nome_schema_envio: string;
    nome_schema_consulta: string;
    url_consulta: string;
    url_envio: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiESocialListarConfiguracoes(payload: Payload) {
    const { data } = await useGet<Response>('esocial/configuracoes/', payload);
    return data;
}
