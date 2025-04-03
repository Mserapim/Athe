import { useGet } from 'api/@base/use-get';
import { ColaboradorEventualModelReturn } from '../modelos/colcadorardor-eventual-model';

interface Payload {
    id: number;
}


export async function apiDefinColaboradorEventual(
    payload: Payload
) {
    const { data } = await useGet<ColaboradorEventualModelReturn>(
        'rh/defin/colaborador-eventual/',
        payload
    );
    return data;
}
