import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { AcquisitionPeriodsStatusEnum } from 'enums/acquisition-periods-status.enum';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

interface Payload extends ListPayload {
    keyword?: string;
    month: number;
    year: number;
    per_page?: number;
}

class ResponseItem {
    pk: number;
    title: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhPvfConfigReportsTypesPayroll(payload: Payload) {
    const { data } = await useGet<Response>(
        'rh/pvf/config/reports/types-payroll/',
        payload
    );
    return data;
}
