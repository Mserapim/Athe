import { useGet } from 'api/@base/use-get';
import { PagamentoModelReturn } from '../modelos/pagamento-model';

interface Payload {
    id: number;
}


export async function apiDefinPagamentoColaboradorEventual(
    payload: Payload
) {
    const { data } = await useGet<PagamentoModelReturn>(
        'rh/defin/pagamento-colaborador/',
        payload
    );
    return data;
}
