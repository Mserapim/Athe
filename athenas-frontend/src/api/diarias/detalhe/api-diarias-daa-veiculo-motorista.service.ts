import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    destinoId: number;
}

export class ResponseItem {
    motorista: string;
    veiculo_placa: string;
    veiculo_marca: string;
    veiculo_modelo: string;
    veiculo_capacidade_passageiros: number;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiBeneficiarioVeiculoMotorista(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'diarias/beneficiario/destino/veiculo-motorista/',
        payload
    );
    return data;
}