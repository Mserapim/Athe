import { usePost } from 'api/@base/use-post';
import { EnderecoModelReturn } from './endereco-model';

interface Payload {
    id: number;
    tipo_endereco: number;
    tipo_logradouro: number;
    logradouro: string;
    numero: string;
    complemento: string;
    bairro: string;
    cep: string;
    municipio?: number;
    pessoa?: number;
    orgao?: number;
    pais: number;
    exterior?: boolean;
    cidade_exterior?: string;
}


export async function apiRhEnderecolEditar(
    payload: Payload
) {
    const { data } = await usePost<EnderecoModelReturn>(
        'rh/endereco/editar/',
        payload
    );

    return data;
}
