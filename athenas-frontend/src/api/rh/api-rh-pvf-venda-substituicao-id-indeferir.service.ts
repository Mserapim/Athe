import { usePost } from 'api/@base/use-post';

interface Payload {
    itemId: number;
    observation: string;
}

class Response {}

export async function apiRhPvfVendaSubstituicaoIdIndeferir(payload: Payload) {
    const { data } = await usePost<Response>(
        '/rh/pvf/venda-substituicoes/' + payload.itemId + '/indeferir/',
        payload
    );
    return data;
}
