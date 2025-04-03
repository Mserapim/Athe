import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { AcquisitionPeriodsStatusEnum } from 'enums/acquisition-periods-status.enum';

interface Payload extends ListPayload {
    page?: number;
    config: number;
    per_page?: number;
    keyword?: string;
}

export class ApiRhPvfMyRightsItemAcquisitionPeriods {
    pk: number;
    group_period_name: string;
    start_date_acquisition: Date;
    end_date_acquisition: Date;
    start_date_fruition: Date;
    days: number;
    booked_days: string;
    balance_available: string;
}

class Response extends ListPaginated<ApiRhPvfMyRightsItemAcquisitionPeriods> {}

export async function apiRhPvfMyRightsAcquisitionPeriods(payload: Payload) {
    const { data } = await useGet<Response>(
        'rh/pvf/myrights/acquisition-periods',
        payload
    );
    return data;
}
