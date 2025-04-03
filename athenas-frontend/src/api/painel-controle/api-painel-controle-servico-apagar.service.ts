import { usePost } from 'api/@base/use-post';

interface Payload {
    id?: number;
    name?: string;
    command?: string;
    description?: string;
    classcode?: string;
}

export class ApiPainelControleServicoApagar {
    id: number;
    name?: string;
    command?: string;
    description?: string;
    classcode?: string;
}

export async function apiPainelControleServicoApagar(
    payload: Payload
) {
    const { data } =
        await usePost<ApiPainelControleServicoApagar>(
            'adm/servico/apagar/',
            payload
        );

    return data;
}