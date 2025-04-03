import { usePost } from 'api/@base/use-post';

interface Payload {
    id: number;
    nome: string;
    descricao: string;
    ordem: number;
    sigla: string;
    icone: string;
    situacao: 'ATIVO' | 'INATIVO';
}

export class ApiPainelControleControleAcessoModuloAtualizar {
    id: number;
    nome: string;
    descricao: string;
    sigla: string;
    icone: string;
    ordem: number;
    situacao: 'ATIVO' | 'INATIVO';
}

export async function apiPainelControleControleAcessoModuloAtualizar(
    payload: Payload
) {
    const { data } =
        await usePost<ApiPainelControleControleAcessoModuloAtualizar>(
            'painel-controle/controle-acesso/modulo/editar/',
            payload
        );

    return data;
}
