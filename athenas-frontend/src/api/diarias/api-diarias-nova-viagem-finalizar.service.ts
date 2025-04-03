import { usePost } from 'api/@base/use-post';

interface Payload {
    id: number;
    
}

export async function apiDiariasViagemFinalizar(
    payload: Payload
) {
    const data = await usePost<any>(
        'diarias/minhas-diarias/viagem/finalizar/',
        payload
    );
    return data;
}
