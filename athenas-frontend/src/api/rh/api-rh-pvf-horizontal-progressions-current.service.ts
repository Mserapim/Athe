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

export class ApiRhPvfHorizontalProgressionsCurrentResponseItem {
    pk: number;
    mov_posse: string;
    reference: string;
    expected_date: Date;
}

class Response extends ListPaginated<ApiRhPvfHorizontalProgressionsCurrentResponseItem> {}

export async function apiRhPvfHorizontalProgressionsCurrent(payload: Payload) {
    const { data } = await useGet<Response>(
        'rh/pvf/horizontal-progressions/current',
        payload
    );
    return data;
}
