import { ListPaginated } from 'api/@base/list-paginated';
import { useGet } from 'api/@base/use-get';

export interface Payload extends ListPaginated<any> {
    palavra_chave?: string;
    usuario_id?:number;
    modulo_id?:number;
}

export class ApiPainelControleControleAcessoMenuConfigsItem {
    id: number;
    created_at: Date;
    modified_at: Date;
    nome: string;
    descricao: string;
    situacao: 'ATIVO' | string;
    created_by: number;
    modified_by: number;
    servidores: number[];
}

export class ApiPainelControleControleAcessoUsuarioGrupos extends ListPaginated<ApiPainelControleControleAcessoMenuConfigsItem> {}

export async function apiPainelControleControleAcessoUsuarioGrupos(
    payload: Payload
) {
    const { data } = await useGet<ApiPainelControleControleAcessoUsuarioGrupos>(
        'painel-controle/controle-acesso/usuario/grupos',
        payload
    );

    return data;
}
