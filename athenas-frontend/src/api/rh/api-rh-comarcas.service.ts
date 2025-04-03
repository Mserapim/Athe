import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { AcquisitionPeriodsStatusEnum } from 'enums/acquisition-periods-status.enum';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

interface Payload extends ListPayload {
    keyword?: string;
    page?: number;
    per_page?: number;
}

export class ApiRhComarcasItem {
    id: number;
    nome: string;
}

class Response extends ListPaginated<ApiRhComarcasItem> {}

export async function apiRhComarcas(payload: Payload) {
    const { data } = await useGet<Response>('rh/comarcas/', payload);
    return data;
}
