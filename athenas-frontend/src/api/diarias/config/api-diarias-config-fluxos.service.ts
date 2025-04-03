import { ListPaginated } from 'api/@base/list-paginated';
import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';

export class ApiDiariasConfigFluxosPayload extends ListPayload {
    id: number;
    ordem: number;
    etapa: number;
    situacao: number;
    notificar: boolean;
    situacao_display: string;
    etapa_display: string;
}

export class ApiDiariasConfigFluxosItem {
    id: number;
    ordem: number;
    etapa: number;
    situacao: number;
    notificar: boolean;
    situacao_display: string;
    etapa_display: string;
    fluxo_display: string;
    condicionais: Condicionais[];
    condicionais_descricao: string;
    criado_por_username: string;
    created_at: Date;
    modificado_por_username: string;
    modified_at: Date;
}

export interface Condicionais {
    id: number;
    condicionais: number[]; 
    descricao: string[];
}

export class ApiDiariasConfigFluxos extends ListPaginated<ApiDiariasConfigFluxosItem> {}

export async function apiDiariasConfigFluxos(
    payload: ApiDiariasConfigFluxosPayload
) {
    const { data } = await useGet<ApiDiariasConfigFluxos>(
        'diarias/config/fluxos/',
        payload
    );

    return data;
}
