import { usePost } from 'api/@base/use-post';
import { TelefoneModelReturn } from './telefone-model';

interface Payload {
    pessoa?: number;
    orgao_geral?: number;
    tipo_telefone: number;
    numero: string;
    principal: boolean;
    publico: boolean;

}


export async function apiRhTelefoneCriar(
    payload: Payload
) {
    const { data } = await usePost<TelefoneModelReturn>(
        'rh/telefone/criar/',
        payload
    );

    return data;
}
