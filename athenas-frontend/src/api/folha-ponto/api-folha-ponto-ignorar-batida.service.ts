import { usePost } from 'api/@base/use-post';

interface Payload {
    marcacao_id?: string | number;
}

export class ApiFolhaPontoIgnorarBatida {
    resposta?: string;
}

export async function apiFolhaPontoIgnorarBatida(payload: Payload) {
    const { data } = await usePost<ApiFolhaPontoIgnorarBatida>(
        'folha-ponto/ignorar-batida/',
        payload
    );

    return data;
}
