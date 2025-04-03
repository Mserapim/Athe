import { ListPaginated } from '../@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    menu_id?: number;
    servidor_id?: number;
}

export class ApiPainelControleControleAcessoUsuarioMenuAtualizarFavoritosItem {
    nome: string;
    descricao: string;
    situacao: 'ATIVO';
    ordem: number;
    icone: string;
    url: string;
    created_by: number;
    modified_by: number;
    grupo: number;
    servidores_favoritos: number[];
}

export class ApiPainelControleControleAcessoUsuarioMenuAtualizarFavoritos extends ListPaginated<ApiPainelControleControleAcessoUsuarioMenuAtualizarFavoritosItem> {}

export async function apiPainelControleControleAcessoUsuarioMenuAtualizarFavoritos(
    payload: Payload
) {
    const { data } =
        await usePost<ApiPainelControleControleAcessoUsuarioMenuAtualizarFavoritos>(
            '/painel-controle/controle-acesso/usuario/menu/atualizar-favoritos/',
            payload
        );

    return data;
}
