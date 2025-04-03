import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    id?: number;
    palavra_chave?: string;
    status?: boolean;
    situacao?:string;
    cat_func?: string;
    lotacao?: number;
}

export class ApiPainelControleControleAcessoUsuariosItem {
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

export class ApiPainelControleControleAcessoUsuarios extends ListPaginated<ApiPainelControleControleAcessoUsuariosItem> {}

export async function apiPainelControleControleAcessoUsuarios(payload: Payload) {
    const { data } = await useGet<ApiPainelControleControleAcessoUsuarios>(
        'painel-controle/controle-acesso/usuarios/',
        payload
    );

    return data;
}
