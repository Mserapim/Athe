import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

export interface PayloadGrupoUsuario extends ListPaginated<any> {
    id?: number;
    palavra_chave?: string;
    usuario_grupo_id?: number;
    usuario_id?:number
}

export class ApiPainelControleControleAcessoGrupoUsuariosItem {
    id: number;
    matricula: number;
    nome: string;
    username: string;
    status: boolean;
    unicode: string;
    categoria_funcional: string;
    cargo: string;
    lotacao: string;
    qtd_grupos: number;
    qtd_menus: number;
}

export class ApiPainelControleControleAcessoGrupoUsuarios extends ListPaginated<ApiPainelControleControleAcessoGrupoUsuariosItem> {}

export async function apiPainelControleControleAcessoGrupoUsuarios(payload: PayloadGrupoUsuario) {
    const { data } = await useGet<ApiPainelControleControleAcessoGrupoUsuarios>(
        'painel-controle/controle-acesso/grupo/usuarios/',
        payload
    );

    return data;
}
