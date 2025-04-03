import { usePost } from 'api/@base/use-post';

interface Payload {
    id?: number;
}

export class ApiPainelControleClasscodeApagar {
    id: number;
    slug: string;
    path: string;
    title: string;
    description: string;
    name_object: string;
    typeof: string;
}

export async function apiPainelControleClasscodeApagar(
    payload: Payload
) {
    const { data } =
        await usePost<ApiPainelControleClasscodeApagar>(
            'adm/classcode/apagar/',
            payload
        );

    return data;
}
