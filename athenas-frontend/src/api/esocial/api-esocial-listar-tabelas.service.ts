import {ListPayload} from "../@base/list-payload";
import {DateTime} from "luxon";
import {ListPaginated} from "../@base/list-paginated";
import {useGet} from "../@base/use-get";

interface Payload extends ListPayload {
    keyword: string;
}

class ResponseItem {
    id: number;
    titulo: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiESocialListarTabelas() {
    const { data } = await useGet<Response>('esocial/tabelas/');
    return data;
}
