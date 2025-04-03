import { useGet } from 'api/@base/use-get';


export async function apiDiariaPermissao() {
    const { data}  = await useGet(
        'diarias/minhas-diarias/permissao/',
    );
    return data.result;
}