import { usePost } from 'api/@base/use-post';

interface Payload {
    id: number;
    beneficiarios_ids: number[];
    
}

export async function apiDiariasViagemCancelar(
    payload: Payload
) {
    const data = await usePost<any>(
        'diarias/minhas-diarias/viagem/cancelar/',
        payload
    );
    return data;
}
