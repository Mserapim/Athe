import { usePost } from 'api/@base/use-post';

interface Payload {
    beneficiarios: number[];
    id: number;
}


export async function apiDiariasClonarDestino(
    payload: Payload
) {
    const { data } = await usePost(
        'diarias/viagem/destino/clonar/',
        payload
    );
    return data;
}
