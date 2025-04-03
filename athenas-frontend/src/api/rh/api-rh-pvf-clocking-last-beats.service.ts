import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { AcquisitionPeriodsStatusEnum } from 'enums/acquisition-periods-status.enum';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

interface Payload extends ListPayload {}

export class ApiRhPvfClockingLastBeatsItem {
    pk: number;
    hour: string;
    date: Date;
    name: string;
}

class Response extends ListPaginated<ApiRhPvfClockingLastBeatsItem> {}

export async function apiRhPvfClockingLastBeats(payload: Payload) {
    const { data } = await useGet<Response>(
        'rh/pvf/clocking/last-beats',
        payload
    );
    return data;
}
