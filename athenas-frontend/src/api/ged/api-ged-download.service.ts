import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    file_id: string;
}

class Response {}

export async function apiGedDownload(payload: Payload) {
    const { data } = await useGet<Response>('/ged/download/', payload);
    return data;
}
