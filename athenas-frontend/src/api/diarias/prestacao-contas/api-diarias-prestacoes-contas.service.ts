import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { DateTime } from 'luxon';

export interface Payload extends ListPayload {
    palavra_chave?: string;
    status?: string[];
    beneficiario_id?: number;
    servidores?: number[];

}

export class ResponseItem {
    id: number;
    anexos: any[];
    assinado_por_nome: string;
    created_at: DateTime;
    modified_at: DateTime;
    assinado_em: DateTime;
    viagem_realizada: boolean;
    viagem_total: boolean;
    data_limite: Date;
    data_entrega: Date;
    data_validacao: Date;
    status: string;
    status_display: string;
    obs_servicos_executados: string;
    obs_resultado: string;
    obs_anlaise: string;
    created_by: number;
    modified_by: number;
    assinado_por: number;
    beneficiario: number;
    avaliador: number;
    beneficiario_nome: string;
    beneficiario_matricula: number;
    beneficiario_situcacao: string;
    beneficiario_categoria_funcional: string;
    status_servidor: boolean;
    valor_devolvido: number;
    avaliador_nome: string;
}

class Response extends ListPaginated<ResponseItem> { }

export async function apiDiariasPrestacoesContas(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        'diarias/prestacoes-contas/',
        payload
    );
    return data;
}
