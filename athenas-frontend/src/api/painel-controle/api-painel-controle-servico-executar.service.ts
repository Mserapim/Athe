import { usePost } from 'api/@base/use-post';

interface Payload {
    id: number;
}

export class ApiPainelControleServicoExecutar {
    id: number;
}

export async function apiPainelControleServicoExecutar(
    payload: Payload
) {
    const { data } = await usePost<ApiPainelControleServicoExecutar>(
        'adm/servico/executar-servico/',
        payload
    );

    return data;
}
