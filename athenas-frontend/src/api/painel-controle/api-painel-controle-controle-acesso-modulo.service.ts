import { useGet } from 'api/@base/use-get';

interface Payload {
    id?: number;
}

export class ApiPainelControleControleAcessoModulo {
    id: number;
    nome: string;
    descricao: string;
    sigla: string;
    icone: string;
    ordem: number;
    situacao: 'ATIVO' | 'INATIVO';
}

export async function apiPainelControleControleAcessoModulo(payload: Payload) {
    const { data } = await useGet<ApiPainelControleControleAcessoModulo>(
        'painel-controle/controle-acesso/modulo/',
        payload
    );

    return data;
}
