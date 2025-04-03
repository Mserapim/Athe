import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    keyword?: string;
}

export class ApiVdfConfigTipoFolgaServiceResponseItem {
    label: string;
    value: number;
}

class Response extends ListPaginated<ApiVdfConfigTipoFolgaServiceResponseItem> {}

export async function apiVdfConfigTipoFolgaService(payload: Payload) {
    const { data } = await useGet<Response>('vdf/config-tipos-folgas', payload);
    return data;
}
