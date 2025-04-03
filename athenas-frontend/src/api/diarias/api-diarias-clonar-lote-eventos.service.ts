import { usePost } from 'api/@base/use-post';

interface Payload {
    beneficiario_base: number;
    beneficiarios: number[];
}


export async function apiDiariasClonarLoteEvento(
    payload: Payload
) {
    const { data } = await usePost(
        'diarias/viagem/evento/clonar/lote/',
        payload
    );
    return data;
}
