import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    competence: string;
}

class Response {
    uuid: string;
}

export async function apiReportRhPvfDeliveryPointSheetService(
    payload: Payload
) {
    const { data } = await usePost<Response>(
        'report/rh/pvf/folha-ponto/',
        payload
    );
    return data;
}
