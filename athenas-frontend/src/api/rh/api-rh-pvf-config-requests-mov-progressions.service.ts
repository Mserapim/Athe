import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { AcquisitionPeriodsStatusEnum } from 'enums/acquisition-periods-status.enum';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

interface Payload extends ListPayload {
    keyword: string;
    page: number;
    per_page: number;
}

class ResponseItem {
    pk: number;
    mov_posse: string;
    reference: string;
    expected_date: Date;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhPvfConfigRequestsMovProgressions(payload: Payload) {
    const { data } = await useGet<Response>(
        'rh/pvf/config/requests/mov-progressions',
        payload
    );
    return data;
}
