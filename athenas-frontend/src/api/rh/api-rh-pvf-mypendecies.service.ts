import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { PendingTypeEnum } from 'enums/pending-type.enum';

interface Payload {
    keyword?: string;
    per_page?: number;
}

export class ApiRhPvfMypendeciesResponseItem {
    title: string;
    message: string;
    type: PendingTypeEnum;
    value: any;
}

class Response extends ListPaginated<ApiRhPvfMypendeciesResponseItem> {}

export async function apiRhPvfMypendeciesService(payload: Payload) {
    const { data } = await useGet<Response>('/rh/pvf/mypendecies', payload);
    return data;
}
