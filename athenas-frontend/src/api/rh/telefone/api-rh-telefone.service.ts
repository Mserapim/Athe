import { useGet } from 'api/@base/use-get';
import { TelefoneModelReturn } from './telefone-model';

interface Payload {
    id: number;
}


export async function apiRhTelefone(
    payload: Payload
) {
    const { data } = await useGet<TelefoneModelReturn>(
        'rh/telefone/',
        payload
    );
    return data;
}
