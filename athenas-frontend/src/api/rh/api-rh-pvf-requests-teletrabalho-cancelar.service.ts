import { usePost } from 'api/@base/use-post';

interface Payload {
    request_ids: string[];
    observation: string;
}

export class ApiRhPvfRequestsTeletrabalhoCancelarResponseItem {}

export async function apiRhPvfRequestsTeletrabalhoCancelar(payload: Payload) {
    const { data } =
        await usePost<ApiRhPvfRequestsTeletrabalhoCancelarResponseItem>(
            '/rh/pvf/requests/teletrabalho/cancelar/',
            payload
        );
    return data;
}
