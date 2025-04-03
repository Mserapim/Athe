import { useGet } from 'api/@base/use-get';
import { ListPaginated } from '../@base/list-paginated';
import { Grupo } from '../../core/tipos/grupo';

interface Payload {
    servidor_id?: number;
    modulo_id?: number;
    situacao?: 'ATIVO' | 'INATIVO';
    retornar_favoritos?: boolean;
}

export class ApiPainelControleControleAcessoMenuUsuarioItem {
    id: number;
    pk: number;
    nome: string;
    sigla: string;
    url: string;
    situacao: string;
    icone: string;
    acoes: string[];
    grupos: Grupo[];
    menus_favoritos: {
        id: number;
        nome: string;
        url: string;
        icone?: string;
    }[];
}

export class ApiPainelControleControleAcessoMenuUsuario extends ListPaginated<ApiPainelControleControleAcessoMenuUsuarioItem> {}

export async function apiPainelControleControleAcessoMenuUsuario(
    payload: Payload
) {
    const { data } = await useGet<ApiPainelControleControleAcessoMenuUsuario>(
        '/painel-controle/controle-acesso/menu/usuario/',
        payload
    );

    return data;
}
