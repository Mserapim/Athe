import { usePost } from 'api/@base/use-post';

interface Payload {
    ano_inicial?: number | null;
    ano_final?: number | null;
    servidor?: number | null;
}


export async function apiDiariasImportarSisdias(
    payload: Payload
) {
    const { data } = await usePost(
        'diarias/importar/',
        payload
    );
    return data;
}
