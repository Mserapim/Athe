import { usePost } from 'api/@base/use-post';

interface Payload {
    id: number;
    name?: string;
    command?: string;
    description?: string;
    classcode?: number;
}

export class ApiPainelControleServicoEditar {
    id: number;
    name?: string;
    command?: string;
    description?: string;
    classcode?: number;
    classcode_path?: string;
}

export async function apiPainelControleServicoEditar(
    payload: Payload
) {
    const { data } = await usePost<ApiPainelControleServicoEditar>(
        'adm/servico/editar/',
        payload
    );

    return data;
}
