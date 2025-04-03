import { usePost } from 'api/@base/use-post';

interface Payload {
    usuario: string;
    senha: string;
}


export async function apiAssinadorSuite(
    payload: Payload
) {
    const { data } = await usePost(
        'adm/assinador/',
        payload
    );
    return data;
}
