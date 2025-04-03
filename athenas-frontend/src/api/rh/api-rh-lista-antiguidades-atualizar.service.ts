import { usePost } from 'api/@base/use-post';

interface Payload {

}

export class ApiRhListaAntiguidadesAtualizar {

}

export async function apiRhListaAntiguidadesAtualizar(
    payload: Payload
) {
    const { data } =
        await usePost<ApiRhListaAntiguidadesAtualizar>(
            'rh/antiguidades/atualizar_lista/',
            payload
        );

    return data;
}
