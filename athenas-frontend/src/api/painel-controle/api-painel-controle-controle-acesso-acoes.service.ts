import { ListPaginated } from 'api/@base/list-paginated';
import { useGet } from 'api/@base/use-get';

interface Payload {
}

export class ApiPainelControleControleAcessoAcoes extends ListPaginated<string> {}

export async function apiPainelControleControleAcessoAcoes(
    payload: Payload
) {
    const { data } = await useGet<ApiPainelControleControleAcessoAcoes>(
        'painel-controle/controle-acesso/acoes/',
        payload
    );

    return data.results;
}