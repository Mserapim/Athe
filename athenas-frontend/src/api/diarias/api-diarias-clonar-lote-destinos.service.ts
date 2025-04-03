import { usePost } from 'api/@base/use-post';

interface Payload {
    beneficiario_base: number;
    beneficiarios: number[];
}


export async function apiDiariasClonarLoteDestino(
    payload: Payload
) {
    const { data } = await usePost(
        'diarias/viagem/destino/clonar/lote/',
        payload
    );
    return data;
}
