import { ListPaginated } from 'api/@base/list-paginated';
import { useGet } from 'api/@base/use-get';

interface Payload {
}

interface Situacao {
    value: number;
    label: string;
}

export class ApiDiariasConfigSituacoes extends ListPaginated<Situacao[]> {}

export async function apiDiariasConfigSituacoes(
    payload: Payload
) {
    const { data } = await useGet<ApiDiariasConfigSituacoes>(
        'diarias/config/situacoes/',
        payload
    );

    return data.results;
}