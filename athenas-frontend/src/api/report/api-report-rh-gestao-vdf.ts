import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';

interface Payload extends ListPayload {
    keyword?: string;
    acao_inicio_em?: Date | string
    acao_fim_em?: Date | string
    categorias?: string[] | string
    situacoes?: string[] | string
    solicitacao_fim_em?: Date | string
    solicitacao_inicio_em?: Date | string
    tipos_acoes?: string[] | string
    tipos_solicitacoes?: string[] | string
    usuarios?: string[] | string 
}

export class ApiReportRhGestaoVdfResponseItem {
    message: string;
    success: boolean;
    uuid: string;
}

export async function apiReportRhGestaoVdfService(payload: Payload) {
    const { data } = await useGet<ApiReportRhGestaoVdfResponseItem>(
        '/report/rh/gestao/vdf/',
        payload
    );
    return data;
}
