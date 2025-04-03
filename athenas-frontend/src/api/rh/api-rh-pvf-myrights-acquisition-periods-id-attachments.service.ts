import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    id: number;
}

export class ApiRhPvfMyRightsAcquisitionPeriodsIdAttachmentsResponseItem {
    pk: number;
    acquisition_period_name: string;
    description: string;
    information: string;
    start_date: Date;
    end_date: Date;
    days: 0;
}

class Response extends ListPaginated<ApiRhPvfMyRightsAcquisitionPeriodsIdAttachmentsResponseItem> {}

export async function apiRhPvfMyRightsAcquisitionPeriodsIdAttachments(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'rh/pvf/myrights/acquisition-periods/' + payload.id + '/attachments/'
    );
    return data;
}
