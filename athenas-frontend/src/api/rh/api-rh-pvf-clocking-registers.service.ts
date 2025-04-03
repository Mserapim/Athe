import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {}

class Response {}

export async function apiRhPvfClockingRegister(payload: Payload) {
    const { data } = await usePost<Response>(
        'rh/pvf/clocking/registers/',
        payload
    );
    return data;
}
