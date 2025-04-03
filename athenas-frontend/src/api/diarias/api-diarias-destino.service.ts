import { DateTime } from 'luxon';
import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    id: number;
}

export class ResponseItem {
    id: number;
    beneficiario: number;
    evento: number;
    created_at: DateTime;
    modified_at: DateTime;
    forma_deslocamento: string;
    pref_turno_ida: string;
    data: string;
    uf_origem: number;
    municipio_origem: number;
    uf_destino: number;
    municipio_destino: number;
    uf_origem_sigla: string;
    uf_destino_sigla: string;
    distancia_m: number;
    distancia_km: number;
    com_motorista: boolean;
    veiculo_daa: boolean;

    uf_origem_display: string;
    uf_destino_display: string;
    municipio_origem_display: string;
    municipio_destino_display: string;
    forma_deslocamento_display: string;
    pref_turno_ida_display: string;
    evento_display: string;

}

class Response extends ListPaginated<ResponseItem> {}

export async function apiDiariasDestino(
    payload: Payload
) {
    const { data } = await useGet<ResponseItem>(
        'diarias/viagem/destino/',
        payload
    );
    return data;
}
