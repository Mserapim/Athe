import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

interface Payload {
    mouth?: number;
    year?: number;
    keyword?: string;
    employee_ids?: number[]; //id rh_servidor
    event_type_ids?: number[]; //Id dos tipos de afastamentos
    group_ids?: number[]; //Id dos tipos de afastamentos
}

export class ApiRhPvfEventsResponseItem {
    pk: number;
    start: Date;
    end: Date | string;
    title: string;
    event_type: string;
    group_id: string;
}

class Response extends ListPaginated<ApiRhPvfEventsResponseItem> {}

export async function apiRhPvfEventsService(payload: Payload) {
    const { data } = await useGet<Response>('/rh/pvf/events', payload);
    return data;
}
