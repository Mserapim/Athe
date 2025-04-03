import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { DateTime } from 'luxon';

interface Payload extends ListPayload {
    palavra_chave: string;
}

class ResponseItem {
    id: number;
    name: string;
    cargo: string;
    matricula: number;
    data_primeira_posse: Date;
    data_exercicio: Date;
    dias_trabalhados: number;
    dias_afastados: number;
    data_fim_estagio: Date;
    dias_para_fim_estagio: number;
    lotacao: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiMembrosEstagioProbatorio(payload: Payload) {
    const { data } = await useGet<Response>('rh/mov-carreira/membros-estagio-probatorio/', payload);
    return data;
}
