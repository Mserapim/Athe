import { ListPaginated } from 'api/@base/list-paginated';
import { useGet } from 'api/@base/use-get';

interface Payload {
}

interface Condicional {
    value: number;
    label: string;
}

export class ApiDiariasConfigCondicionais extends ListPaginated<Condicional[]> {}

export async function apiDiariasConfigCondicionais(
    payload: Payload
) {
    const { data } = await useGet<ApiDiariasConfigCondicionais>(
        'diarias/config/condicionais/',
        payload
    );

    return data.results;
}