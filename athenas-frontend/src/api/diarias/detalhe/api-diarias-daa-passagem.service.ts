import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    destinoId: number;
}

export class ResponseItem {
    destino: number;
    nome_companhia: string;
    aeroporto: string;
    numero_bilhete: number;
    data_hora_bilhete: Date;
    anexos: any[];
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiBeneficiarioDaaPassagem(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'diarias/beneficiario/passagem-aerea/',
        payload
    );
    return data;
}