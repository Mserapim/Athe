import {ListPayload} from "../@base/list-payload";
import {DateTime} from "luxon";
import {ListPaginated} from "../@base/list-paginated";
import {useGet} from "../@base/use-get";

interface Payload extends ListPayload {
    keyword: string;
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
    tabela_esocial: string;
    inicio_vigencia: Date;
    fim_vigencia: Date;
    criado_em: DateTime;
    modificado_em: DateTime;
    criado_por: string;
    modificado_por: string;
    choice_filtro: string;
    opcoes_detalhes: ResponseItemOpcoesDetalhe[];
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiESocialListarItensTabela(payload: Payload) {
    const { data } = await useGet<Response>('esocial/itens-tabela/', payload);
    return data;
}
