import { useDelete } from 'api/@base/use-delete';

export interface Payload {
    id: number;
}

export class Response {}

export async function apiRhPvfScalesServerShiftsDeleteService(
    payload: Payload
) {
    const { data } = await useDelete<Response>(
        'rh/pvf/scales/server-shifts/' + payload.id,
        payload
    );
    return data;
}
