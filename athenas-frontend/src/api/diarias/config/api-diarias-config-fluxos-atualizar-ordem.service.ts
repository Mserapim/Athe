import { usePost } from 'api/@base/use-post';


interface FluxoOrdemUpdate {
    id: number;
    novaOrdem: number;
}

interface Payload {
    updates: FluxoOrdemUpdate[];
}

export class ApiDiariasConfigFluxosAtualizarOrdem {
    updates: FluxoOrdemUpdate[];
}

export async function apiDiariasConfigFluxosAtualizarOrdem(
    payload: Payload
) {
    const { data } = 
        await usePost<ApiDiariasConfigFluxosAtualizarOrdem>(
        'diarias/config/fluxos/atualizar-ordem',
        payload
    );

    return data;
}