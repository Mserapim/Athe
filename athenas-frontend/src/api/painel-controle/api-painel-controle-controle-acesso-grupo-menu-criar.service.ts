import { usePost } from 'api/@base/use-post';

interface Payload {
    modulo: number;
    nome: string;
    descricao: string;
    icone: string;
    ordem: number;
    situacao: 'ATIVO' | string;
}

export class ApiPainelControleControleAcessoGrupoMenuCriar {}

export async function apiPainelControleControleAcessoGrupoMenuCriar(
    payload: Payload
) {
    const { data } =
        await usePost<ApiPainelControleControleAcessoGrupoMenuCriar>(
            'painel-controle/controle-acesso/modulo/grupo-menu/criar/',
            payload
        );

    return data;
}
