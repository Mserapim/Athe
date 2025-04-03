import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    uuid: string;
}

export async function apiReportDownloadService(payload: Payload) {
    const data = (await useGet<any>('/report/download/', payload)) as any;
    return data;
}
