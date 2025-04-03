import { DateTime } from 'luxon';
import { ListPayload } from 'api/@base/list-payload';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    beneficiario: number;
    evento: number;
    forma_deslocamento: string;
    pref_turno_ida: string;
    data: Date;
    uf_origem: number;
    municipio_origem: number;
    uf_destino: number;
    municipio_destino: number;
    com_motorista: boolean;
    veiculo_daa: boolean;
}

export class ResponseItem {
    id: number;
    evento: number;
    beneficiario: number;
    created_at: DateTime;
    modified_at: DateTime;
    forma_deslocamento: string;
    pref_turno_ida: string;
    data: Date;
    uf_origem: number;
    municipio_origem: number;
    uf_destino: number;
    municipio_destino: number;
    distancia_m: number;
    distancia_km: number;
    com_motorista: boolean;
    veiculo_daa: boolean;

    uf_origem_display: string;
    uf_destino_display: string;
    municipio_origem_display: string;
    municipio_destino_display: string;
    forma_deslocamento_display: string;
    evento_display: string;

}

class Response extends ListPaginated<ResponseItem> {}

export async function apiDiariasDestinoCriar(
    payload: Payload
) {
    const { data } = await usePost<Response>(
        'diarias/viagem/destino/criar/',
        payload
    );
    return data;
}
