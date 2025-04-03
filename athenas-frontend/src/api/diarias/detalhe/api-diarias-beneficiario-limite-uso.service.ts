import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    beneficiario_id: number;
    ano?: number;
    meses?: number[];
}

interface LimiteAnual {
    [motivo: string]: {
        motivos: string;
        limite: number;
        uso: number;
    };
}

interface LimiteMensal {
    [motivo: string]: {
        motivos: string;
        limite: number;
        uso: number;
    };
}

export class LimiteUsoDiariasResponse {
    tipo: string;
    ano: number;
    mensal: { [mes: string]: LimiteMensal };
    anual: LimiteAnual;
}
class Response extends ListPaginated<LimiteUsoDiariasResponse> {}

export async function apiDiariasLimiteUso(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'diarias/beneficiario/limite-uso-diarias',
        payload
    );
    return data;
}
