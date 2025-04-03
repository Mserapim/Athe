import { usePost } from 'api/@base/use-post';

interface Payload {
    nome: string;
    descricao: string;
    situacao: 'ATIVO' | 'INATIVO' | string;
    grupo_padrao: boolean;
}

export class ApiPainelControleControleAcessoGrupoCriar {
    pk: number;
    nome: string;
    descricao: string;
    situacao: 'ATIVO' | string;
    grupo_padrao: boolean;
}

export async function apiPainelControleControleAcessoGrupoCriar(
    payload: Payload
) {
    const { data } = await usePost<ApiPainelControleControleAcessoGrupoCriar>(
        'painel-controle/controle-acesso/grupo/criar/',
        payload
    );

    return data;
}
