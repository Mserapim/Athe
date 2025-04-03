import { ListPaginated } from 'api/@base/list-paginated';
import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';

export class ApiPainelControleControleAcessoGrupoPayload extends ListPayload {
    id?: number;
    menus_qtd?: number | string;
    usuarios_qtd?: number | string;
    nome?: string;
    descricao?: string;
    situacao?: string;
    grupo_padrao?: boolean;
}

export class ApiPainelControleControleAcessoGrupo {
    id?: number;
    menus_qtd?: number | string;
    usuarios_qtd?: number | string;
    nome?: string;
    descricao?: string;
    situacao?: 'ATIVO' | 'INATIVO';
    grupo_padrao?: boolean;
}

export async function apiPainelControleControleAcessoGrupo(
    payload: ApiPainelControleControleAcessoGrupoPayload
) {
    const { data } = await useGet<ApiPainelControleControleAcessoGrupo>(
        'painel-controle/controle-acesso/grupo/',
        payload
    );

    return data;
}
