import {ListPayload} from "../../@base/list-payload";
import {DateTime} from "luxon";
import {ListPaginated} from "../../@base/list-paginated";
import {useGet} from "../../@base/use-get";

interface Payload extends ListPayload {
    keyword: string;
}

class ResponseItem {
    valor: number;
    texto: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiESocialListarStatus() {
    const { data } = await useGet<Response>('esocial/config/status');
    return data;
}
