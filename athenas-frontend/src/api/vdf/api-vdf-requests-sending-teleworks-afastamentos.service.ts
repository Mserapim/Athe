import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    id?: number;
    keyword?: number;
    ano: number;
    mes: number;
    servidor_id?: number;
}

export class ApiVdfRequestsSendingTeleworksAfastamentosItem {
    id: number;
    tipo: string;
    created_at: Date;
    modified_at: Date;
    texto: string;
    anota: boolean;
    data_alteracao: Date;
    my_type: string;
    remunerado: boolean;
    concessao_durante_estagio_prob: boolean;
    efetivo_exercicio: boolean;
    suspensao_estagio_prob: boolean;
    suspensao_contagem_ferias: boolean;
    prorroga_progressao: boolean;
    data_inicio: Date;
    data_fim: Date;
    data_prevista: Date;
    motivo: number;
    estado: number;
    alteracao: number;
    agendado_arquimedes: boolean;
    situation_unicode: string;
    annotation_class: string;
    interrupt_vacation: boolean;
    status_change_date: Date;
    event_esocial: number;
    origin_register: number;
    desconta_tempo: number;
    total_parcial: number;
    total_desconto: number;
    created_by: number;
    modified_by: number;
    servidor: number;
    anotacao_geral: number;
    publicacao_movimentacao: number;
    publicacao_alteracao: number;
    publicacao_fim: number;
}

export class ApiVdfRequestsSendingTeleworksAfastamentos extends ListPaginated<ApiVdfRequestsSendingTeleworksAfastamentosItem> {}

export async function apiVdfRequestsSendingTeleworksAfastamentos(
    payload: Payload
) {
    const { data } = await useGet<ApiVdfRequestsSendingTeleworksAfastamentos>(
        'vdf/requests/sending/teleworks/afastamentos/',
        payload
    );
    return data;
}
