import { ListPaginated } from 'api/@base/list-paginated';
import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';

export class ApiPainelControleControleAcessoIconsPayload extends ListPayload {
    keyword?: string;
}


export async function apiPainelControleControleAcessoIcons(
    payload: ApiPainelControleControleAcessoIconsPayload
) {
    const { data } = await useGet<ListPaginated<string>>(
        'painel-controle/controle-acesso/icons/',
        payload
    );

    return data;
}
