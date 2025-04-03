import { usePost } from 'api/@base/use-post';

interface Payload {
    beneficiarios: number[];
    id: number;
}


export async function apiDiariasClonarEvento(
    payload: Payload
) {
    const { data } = await usePost(
        'diarias/viagem/evento/clonar/',
        payload
    );
    return data;
}
