import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { DateTime } from 'luxon';

interface Payload extends ListPayload {
    membroId: number;
}

class ResponseItem {
    id: number;
    tipo: string;
    data_inicio: Date;
    data_fim: Date;
    qtd_dias: number;
    servidor_unicode: string;
    situation_unicode: string;
    afastamento_unicode: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiAfastamentosMembrosEstagioProbatorio(payload: Payload) {
    const { data } = await useGet<Response>('rh/mov-carreira/membros-estagio-probatorio/afastamentos/', payload);
    return data;
}
