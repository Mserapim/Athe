import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    keyword?: string;
}

interface ApiAuditoriaModelosLogsServiceResponseItem {
    label: string;
    value: number;
}

class Response extends ListPaginated<ApiAuditoriaModelosLogsServiceResponseItem> {}

export async function apiAuditoriaModelosLogs(payload: Payload) {
    const { data } = await useGet<Response>('auditoria/logs/modelos/', payload);
    return data;
}
