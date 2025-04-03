import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

export interface Payload extends ListPayload {
    palavra_chave?: string;
}

export class ChoicesItem {
    valor: number;
    display: string;
}

class Response extends ListPaginated<ChoicesItem> {}

export async function apiDefinNarurezaAtividade(
    payload: Payload
) {


    const { data } = await useGet<Response>(
        'standard/choices-formulario/',
        {...payload,
            name:'NATURE_ACTIVITY',
            app:'defin'
        }
    );
    return data;
}
