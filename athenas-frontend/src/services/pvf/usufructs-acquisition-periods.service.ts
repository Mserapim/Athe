import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { AcquisitionPeriodsStatusEnum } from 'enums/acquisition-periods-status.enum';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

interface Payload extends ListPayload {
    page: number;
    type_usufruct: TypeUsufructEnum;
}

class ResponseItem {
    group_period: number;
    group_period_name: string;
    status: AcquisitionPeriodsStatusEnum;
    status_name: string;
    days: number;
    balance_available: string;
    start_date_acquisition: Date;
    end_date_acquisition: Date;
    start_date_fruition: Date;
}

class Response extends ListPaginated<ResponseItem> {}

export async function pvfUsufructsAcquisitionPeriods(payload: Payload) {
    const { data } = await useGet<Response>(
        '/rh/pvf/usufructs/acquisition_periods/',
        payload
    );
    return data;
}
