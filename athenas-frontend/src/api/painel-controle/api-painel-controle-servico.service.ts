import { useGet } from 'api/@base/use-get';

interface Payload {
    id: number;
}

export class Response {
    id?: number;
    name?: string;
    command?: string;
    description?: string;
    classcode?: number;
    classcode_path?: string;
}

export async function apiPainelControleServico(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'adm/servico/',
        payload
    );

    return data;
}