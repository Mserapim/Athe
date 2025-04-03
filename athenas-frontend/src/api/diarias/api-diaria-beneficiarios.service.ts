import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

export interface Payload extends ListPayload {
    keyword?: string;
    viagem_id: number;
    telaChefeImediato?: boolean;
    exclude?: number[];
}

export class ApiDiariasBeneficiariosResponseItem {
    id:number;
    servidor_unicode: string; 
    conta_bancaria_unicode: string;
    fluxo: number;
    fluxo_unicode: string;
    cargo: string;
    qtd_destinos: number;
    qtd_eventos: number;
    servidor: number;
    gedoc_numero: number;
    qtd_total_diarias: number;
    qtd_total_diarias_deferido: number;
}

class Response extends ListPaginated<ApiDiariasBeneficiariosResponseItem> {}

export async function apiDiariasBeneficiarios(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'diarias/minhas-diarias/beneficiarios/',
        payload
    );
    return data;
}
