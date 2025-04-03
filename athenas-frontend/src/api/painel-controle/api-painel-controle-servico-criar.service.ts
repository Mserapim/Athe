import { usePost } from 'api/@base/use-post';

interface Payload {
    name: string;
    command: string;
    description: string;
    classcode: number;
}

export class ApiPainelControleServicoCriar {
    id: number;
    name?: string;
    command?: string;
    description?: string;
    classcode?: number;
}

export async function apiPainelControleServicoCriar(
    payload: Payload
) {
    const { data } = await usePost<ApiPainelControleServicoCriar>(
        'adm/servico/criar/',
        payload
    );

    return data;
}
