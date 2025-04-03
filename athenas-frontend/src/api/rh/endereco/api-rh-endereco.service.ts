import { useGet } from 'api/@base/use-get';
import { EnderecoModelReturn } from './endereco-model';

interface Payload {
    id: number;
}


export async function apiRhEndereco(
    payload: Payload
) {
    const { data } = await useGet<EnderecoModelReturn>(
        'rh/endereco/',
        payload
    );
    return data;
}
