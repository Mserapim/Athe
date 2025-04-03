import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { AcquisitionPeriodsStatusEnum } from 'enums/acquisition-periods-status.enum';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

interface Payload extends ListPayload {
    keyword?: string;
    per_page?: number;
}

class ResponseItem {}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhPvfConfigReportsPaychecksYears(payload: Payload) {
    const { data } = await useGet<Response>(
        'rh/pvf/config/reports/paychecks/years/',
        payload
    );
    return data;
}
