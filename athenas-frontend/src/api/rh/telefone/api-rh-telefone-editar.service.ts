import { usePost } from 'api/@base/use-post';
import { TelefoneModelReturn } from './telefone-model';

interface Payload {
    id: number;
    pessoa?: number;
    orgao_geral?: number;
    tipo_telefone: number;
    numero: string;
    principal: boolean;
    publico: boolean;
    
}


export async function apiRhTelefoneEditar(
    payload: Payload
) {
    const { data } = await usePost<TelefoneModelReturn>(
        'rh/telefone/editar/',
        payload
    );

    return data;
}
