import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { AcquisitionPeriodsStatusEnum } from 'enums/acquisition-periods-status.enum';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

interface Payload {
    month: number;
    year: number;
    type_report: number;
    team_id: number;
}

class Response {
    message: string;
    uuid: string;
}

export async function apiReportRhPvfCalendar(payload: Payload) {
    const { data } = await usePost<Response>(
        'report/rh/pvf/calendar/',
        payload
    );
    return data;
}
