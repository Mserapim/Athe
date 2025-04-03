import { usePost } from 'api/@base/use-post';


interface Payload {
    id: number;
}

export class ApiDiariasConfigFluxoApagar {
    id: number;
}

export async function apiDiariasConfigFluxoApagar(
    payload: Payload
) {
    const { data } = 
        await usePost<ApiDiariasConfigFluxoApagar>(
        'diarias/config/fluxo/apagar/',
        payload
    );

    return data;
}
