import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {}

class ResponseItem {
    pk: number;
    nome: string;
    matricula: number;
    tipo_posse: string;
    ativo: boolean;
    unicode: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiDiariasMotoristasService(payload: Payload) {
    const { data } = await useGet<Response>(
        'diarias/config/motoristas-diarias/', 
        payload
    );
    return data;
}
