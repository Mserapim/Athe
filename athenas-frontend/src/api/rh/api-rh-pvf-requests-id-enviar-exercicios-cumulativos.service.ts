import { usePost } from 'api/@base/use-post';

interface Payload {
    id: string;
}

class ResponseItem {}

export async function apiRhPvfRequestsIdEnviarExerciciosCumulativos(
    payload: Payload
) {
    const { data } = await usePost<ResponseItem>(
        '/v2/rh/pvf/requests/' + payload.id + '/enviar/exercicios-cumulativos/',
        payload
    );
    return data;
}
