import { ListPaginated } from 'api/@base/list-paginated';
import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';

export class ApiPainelControleControleAcessoMenuMenusConfigsUsuariosPayload extends ListPayload {
    menu_id?: number;
}

export interface ApiPainelControleControleAcessoMenuMenusConfigsUsuariosItem {
    id: number;
    matricula: string;
    nome: string;
    username: string;
    status: boolean;
    grupos: string[];
}

export class ApiPainelControleControleAcessoMenuMenusConfigsUsuarios extends ListPaginated<ApiPainelControleControleAcessoMenuMenusConfigsUsuariosItem> {}

export async function apiPainelControleControleAcessoMenuMenusConfigsUsuarios(
    payload: ApiPainelControleControleAcessoMenuMenusConfigsUsuariosPayload
): Promise<ApiPainelControleControleAcessoMenuMenusConfigsUsuarios> {
    const { data } = await useGet<ApiPainelControleControleAcessoMenuMenusConfigsUsuarios>(
        'painel-controle/controle-acesso/menu/menus-configs/usuarios',
        payload
    );
    return data;
}
