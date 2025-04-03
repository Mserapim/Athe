import {ListPayload} from "../@base/list-payload";
import {ListPaginated} from "../@base/list-paginated";
import {useGet} from "../@base/use-get";

interface Payload extends ListPayload {
    keyword?: string;
}

class ResponseItem {
    id: number;
    cod: number;
    descricao: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiESocialListarEventos(payload: Payload) {
    const { data } = await useGet<Response>('esocial/eventos/', payload);
    return data;
}
