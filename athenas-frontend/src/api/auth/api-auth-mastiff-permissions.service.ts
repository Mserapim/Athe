import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    app: string;
}

class Response {}

export async function authMastiffPermissionsService(payload: Payload) {
    const { data } = await usePost<Response>(
        '/auth/mastiff/permissions/',
        payload
    );
    return data;
}
