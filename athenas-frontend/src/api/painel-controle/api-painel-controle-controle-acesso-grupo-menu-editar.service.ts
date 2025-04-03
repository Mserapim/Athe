import { usePost } from 'api/@base/use-post';

interface Payload {
    id: number;
    modulo?: number;
    nome: string;
    descricao: string;
    icone: string;
    ordem: number;
    situacao: 'ATIVO' | string;
}

export class ApiPainelControleControleAcessoGrupoMenuEditar {}

export async function apiPainelControleControleAcessoGrupoMenuEditar(
    payload: Payload
) {
    const { data } =
        await usePost<ApiPainelControleControleAcessoGrupoMenuEditar>(
            'painel-controle/controle-acesso/modulo/grupo-menu/editar/',
            payload
        );

    return data;
}
