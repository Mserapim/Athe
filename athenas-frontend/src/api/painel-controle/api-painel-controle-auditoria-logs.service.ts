import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { DateTime } from 'luxon';

export interface ApiAuditoriaLogsPayload extends ListPayload {
    keyword?: string;
    modelos?: string[] | string;
    acoes?: string[] | string;
    log_inicio_em?: Date | string;
    log_fim_em?: Date | string;
}

interface ResponseItem {
    id: number;
    objeto_id: number;
    data: string;
    usuario: string;
    endereco_ip: string;
    modelo: {
        id: number;
        display: string;
    };
    modelo_id: number;
    acao: {
        valor: number;
        display: string;
    };
    alteracoes: Record<string, { anterior: string | null; novo: string | null }>[];
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiAuditoriaLogs(payload: ApiAuditoriaLogsPayload) {
    const { data } = await useGet<Response>('auditoria/logs/', payload);
    return data;
}
