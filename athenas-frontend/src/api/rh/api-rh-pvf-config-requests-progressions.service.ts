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
    name: number;
    description: number;
    target_level: string;
    contribution_time: number;
    qtd_documents: number;
    schooling_str: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhPvfConfigMovProgressions(payload: Payload) {
    const { data } = await useGet<Response>(
        'rh/pvf/config/mov-progressions',
        payload
    );
    return data;
}
