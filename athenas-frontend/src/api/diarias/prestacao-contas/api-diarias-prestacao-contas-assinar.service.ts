import { usePost } from 'api/@base/use-post';
import { DateTime } from 'luxon';

interface Payload {
    id: number;
}

export class ResponseItem {
    id: number;
    anexos: any[];
    assinado_por_nome: string;
    created_at:  DateTime;
    modified_at: DateTime;
    assinado_em: DateTime;
    viagem_realizada: boolean;
    viagem_total: boolean;
    data_limite: Date;
    data_entrega: Date;
    status:  string;
    obs_servicos_executados:  string;
    obs_resultado:  string;
    obs_anlaise: string;
    created_by: number;
    modified_by: number;
    assinado_por: number;
    beneficiario: number;
    avaliador: number;
    obs: string;
    valor_devolvido: number;
    avaliador_nome: string;
}

export async function apiDiariasPrestacaoContasAssinar(
    payload: Payload
) {
    const { data } = await usePost<any>(
        'diarias/prestacao-contas/assinar/',
        payload
    );
    return data;
}
