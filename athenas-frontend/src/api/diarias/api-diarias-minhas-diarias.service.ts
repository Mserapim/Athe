import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

export interface Payload extends ListPayload {
    keyword?: string;
    situacoes?: number[];
    tipos_viagem?: string[];
    motivos_viagem?: number[];
    finalidades?: number[];
}

export class ResponseItem {
    id: number;
    tipo_viagem: string;
    hospedagem_anfitriao: boolean;
    motivo_viagem: number;
    finalidade_viagem: number;
    custeada_por: string;
    data_inicio_viagem: Date;
    data_fim_viagem: Date;
    data_solicitacao: Date;
    resumo: string;
    justificativa: string;
    chefes_imediatos: number[];
    servidores_beneficiarios: number[];
    servidores_beneficiarios_unicode: string[];
    fluxo: number;

    aprovador_atual: string;
    tipo_viagem_display: string;
    motivo_viagem_display: string;
    finalidade_viagem_display: string;
    custeada_por_display: string;
    situacao_solicitacao_display: string;
    etapa_solicitacao_display: string;

    solicitante: string;
    solicitante_unicode: string;
    solicitante_servidor: number;

}

class Response extends ListPaginated<ResponseItem> {}

export async function apiDiariasMinhasDiarias(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'diarias/minhas-diarias/',
        payload
    );
    return data;
}
