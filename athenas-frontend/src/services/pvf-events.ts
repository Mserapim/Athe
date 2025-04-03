import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

interface Payload {
    mouth: number;
    year: number;
    register: number; //matricula
    types: number[];
}

export class PvfEventsResponseItem {
    pk: number;
    start: Date;
    end: Date;
    title: string;
    eventType: string;
}

class Response extends ListPaginated<PvfEventsResponseItem> {}

export async function pvfEventsService(payload: Payload) {
    const { data } = await useGet<Response>('/rh/pvf/events', payload);
    return data;
}
