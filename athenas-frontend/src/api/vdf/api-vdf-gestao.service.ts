import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

export interface ApiVdfGestaoServicePayload extends ListPayload {
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
    filtrar_por?: "solicitacao" | "acao"
}

export class ApiVdfGestaoServiceResponseItem {
    id: number
    tipo_solicitacao: string
    mes_referencia: string
    situacao: string
    servidor: string
    aprovador: string
    dias_aguardando_aprovacao: string
    periodo_aquisitivo: string
    historico: {
        acao: string,
        grupo: string,
        servidor: string,
        data: Date
        observacao: string
      }[]
}

class Response extends ListPaginated<ApiVdfGestaoServiceResponseItem> {}

export async function apiVdfGestaoService(payload: ApiVdfGestaoServicePayload) {
    const { data } = await useGet<Response>('vdf/gestao', payload);
    return data;
}
