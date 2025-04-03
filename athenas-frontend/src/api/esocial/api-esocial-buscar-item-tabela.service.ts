import {DateTime} from "luxon";
import {useGet} from "../@base/use-get";

interface Payload {
    id: number;
}

class ResponseItemOpcoesDetalhe {
    id: number;
    titulo: string;
    valor: string;
}

class ResponseItem {
    id: number;
    titulo: string;
    codigo: string;
    info: string;
    descricao: string;
    tabela_esocial: number;
    inicio_vigencia: string;
    fim_vigencia: string;
    criado_em: DateTime;
    modificado_em: DateTime;
    criado_por: string;
    modificado_por: string;
    choice_filtro: string;
    opcoes_detalhes: ResponseItemOpcoesDetalhe[];
}

class Response extends ResponseItem {}

export async function apiESocialBuscarItemTabela(payload: Payload) {
    const { data } = await useGet<Response>('esocial/item-tabela/', payload);
    return data;
}
