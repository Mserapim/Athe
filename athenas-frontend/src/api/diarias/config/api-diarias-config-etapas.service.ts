import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
}

interface Etapa {
    value: number;
    label: string;
}

export class ApiDiariasConfigEtapas extends ListPaginated<Etapa[]> {}

export async function apiDiariasConfigEtapas(
    payload: Payload
) {
    const { data } = await useGet<ApiDiariasConfigEtapas>(
        'diarias/config/etapas/',
        payload
    );

    return data.results;
}