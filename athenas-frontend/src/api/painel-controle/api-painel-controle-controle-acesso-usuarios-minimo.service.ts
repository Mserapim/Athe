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

export class ApiPainelControleControleAcessoUsuariosMinimoItem {
    id: number;
    nome: string;
}

export class ApiPainelControleControleAcessoUsuariosMinimo extends ListPaginated<ApiPainelControleControleAcessoUsuariosMinimoItem> {}

export async function apiPainelControleControleAcessoUsuariosMinimo(payload: Payload) {
    const { data } = await useGet<ApiPainelControleControleAcessoUsuariosMinimo>(
        'painel-controle/controle-acesso/grupo/usuarios/minimo/',
        payload
    );

    return data;
}
