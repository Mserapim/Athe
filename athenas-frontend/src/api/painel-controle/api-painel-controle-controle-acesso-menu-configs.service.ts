import { ListPaginated } from 'api/@base/list-paginated';
import { useGet } from 'api/@base/use-get';

interface Payload {
    menu_id?: number | string;
    usuario_grupo_id?: number | string;
    situacao?: string;
}

export class ApiPainelControleControleAcessoMenuConfigsItem {
    id: number;
    usuario_grupo_nome: string;
    acoes: string[];
    modelo_id: number;
    usuario_grupo: number;
    menu: number;
}

export class ApiPainelControleControleAcessoMenuConfigs extends ListPaginated<ApiPainelControleControleAcessoMenuConfigsItem> {}

export async function apiPainelControleControleAcessoMenuConfigs(
    payload: Payload
) {
    const { data } = await useGet<ApiPainelControleControleAcessoMenuConfigs>(
        'painel-controle/controle-acesso/menu-configs/',
        payload
    );

    return data;
}
