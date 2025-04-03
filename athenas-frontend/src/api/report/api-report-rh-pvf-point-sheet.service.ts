import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { AcquisitionPeriodsStatusEnum } from 'enums/acquisition-periods-status.enum';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

interface Payload {
    month?: number;
    year?: number;
    inicio?: string;
    fim?: string;
}

class Response {
    message: string;
    success: boolean;
    uuid: string;
}

export async function apiReportRhPvfPointSheet(payload: Payload) {
    const { data } = await usePost<Response>(
        'report/rh/pvf/folha-ponto/',
        payload
    );
    return data;
}
