import {ListPayload} from "../@base/list-payload";
import {DateTime} from "luxon";
import {ListPaginated} from "../@base/list-paginated";
import {useGet} from "../@base/use-get";

interface Payload extends ListPayload {
    keyword?: string;
    choice_filtro?: string;
}

class ResponseItem {
    id: number;
    titulo: string;
    valor: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiESocialListarOpcoesTabela(payload: Payload) {
    const { data } = await useGet<Response>('esocial/opcoes-tabela/', payload);
    return data;
}
