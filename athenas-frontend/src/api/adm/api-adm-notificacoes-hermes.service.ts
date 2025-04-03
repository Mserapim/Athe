import { ListPayload } from 'api/@base/list-payload';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';
import { useGet } from 'api/@base/use-get';

export interface Payload extends ListPayload {
    per_page: number;
}

class Response extends ListPaginated<any> {}

export async function apiAdmNotificacoesHermes(payload: Payload) {
    const { data } = await useGet<Response>(
        'adm/notificacoes-hermes/',
        payload
    );
    return data;
}
