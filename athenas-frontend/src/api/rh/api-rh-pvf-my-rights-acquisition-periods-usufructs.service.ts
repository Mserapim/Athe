import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { AcquisitionPeriodsStatusEnum } from 'enums/acquisition-periods-status.enum';

interface Payload extends ListPayload {
    page?: number;
    per_page?: number;
    keyword?: string;
    id?: number;
}

export class ApiRhPvfMyRightsItemAcquisitionPeriodsUsufructs {
    pk: number;
    status_name: string;
    start_date: Date;
    end_date: Date;
    days: number;
}

class Response extends ListPaginated<ApiRhPvfMyRightsItemAcquisitionPeriodsUsufructs> {}

export async function apiRhPvfMyRightsAcquisitionPeriodsUsufructs(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'rh/pvf/myrights/acquisition-periods/' + payload.id + '/usufructs',
        payload
    );
    return data;
}
