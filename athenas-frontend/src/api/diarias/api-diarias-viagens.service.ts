import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

export interface Payload extends ListPayload {
    keyword?: string;
    situacoes?: number[];
    etapas?: number[];
    tipos_viagem?: string[];
    motivos_viagem?: number[];
    finalidades?: number[];
    servidores?: number[];
}

export class ResponseItem {
    id: number;
    tipo_viagem: string;
    hospedagem_anfitriao: boolean;
    motivo_viagem: number;
    finalidade_viagem: number;
    data_inicio_viagem: Date;
    data_fim_viagem: Date;
    data_solicitacao: Date;
    resumo: string;
    justificativa: string;

    solicitante: string;
    solicitante_unicode: string;
    solicitante_servidor: number;
    qtd_beneficiarios: number;

    aprovador_atual: string;
    tipo_viagem_display: string;
    motivo_viagem_display: string;
    finalidade_viagem_display: string;
    custeada_por_display: string;
    situacao_solicitacao_display?: string;
    etapa_solicitacao_display?: string;
    situacao_etapa_atual: string;
    link_informacao: string;
    etapa_fluxo: number;
    
    recebido_por: string;

    possui_excedente: boolean;
    excedente: boolean;
    motorista: boolean;
    importada: boolean;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiDiariasViagens(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'diarias/viagens/',
        payload
    );
    return data;
}
