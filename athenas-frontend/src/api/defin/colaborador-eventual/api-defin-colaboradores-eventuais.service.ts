import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { ColaboradorEventualModelReturn } from '../modelos/colcadorardor-eventual-model';

export interface Payload extends ListPayload {
    palavra_chave?: string;
}

class Response extends ListPaginated<ColaboradorEventualModelReturn> {}

export async function apiDefinColaboradoresEventuais(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'rh/defin/colaboradores-eventuais/',
        payload
    );
    return data;
}
