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

export class ApiRhPvfConfigRequestsAcquisitionPeriodsItem {
    pk: number;
    group_period: number;
    group_period_name: string;
    status: AcquisitionPeriodsStatusEnum;
    status_name: string;
    sale_usufruct: boolean;
    days: number;
    balance_available: number;
    start_date_acquisition: Date;
    end_date_acquisition: Date;
    start_date_fruition: Date;
    group_period_unicode: string;
    saldo_venda: number;
    data_corte_venda: Date;
}

class Response extends ListPaginated<ApiRhPvfConfigRequestsAcquisitionPeriodsItem> {}

export async function apiRhPvfConfigRequestsAcquisitionPeriods(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'rh/pvf/config/requests/acquisition-periods/',
        payload
    );
    return data;
}
