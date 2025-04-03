import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { DateTime } from 'luxon';

interface Payload extends ListPayload {
    keyword?: string;
    id?: number;
}

class ResponseItem {
    id: number;
    description: string;
    task_uuid: string;
    started_task: DateTime;
    finished_task: DateTime;
    message: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiPainelControleMensagens(payload: Payload) {
    const { data } = await useGet<Response>(`adm/historico-servico/${payload.id}/mensagens/`, payload);
    return data;
}
