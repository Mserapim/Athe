import { usePost } from 'api/@base/use-post';
import { ColaboradorEventualModelReturn } from '../modelos/colcadorardor-eventual-model';

interface Payload {
    id: number;
}


export async function apiDefinPagamentoColaboradorEventualApagar(
    payload: Payload
) {
    const { data } = await usePost<ColaboradorEventualModelReturn>(
        'rh/defin/pagamento-colaborador/apagar/',
        payload
    );

    return data;
}
