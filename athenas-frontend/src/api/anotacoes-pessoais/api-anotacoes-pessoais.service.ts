import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

export interface Payload extends ListPayload {
    keyword?: string;
    exportar: string;
    sincrono?: boolean;
    servidor_ids?: number[];
    tipos_anotacao?: number[];
    tipos_documento?: number[];
}

export class ApiAnotacoesPessoaisResponseItem {
    id: number;
    created_at: string;
    texto: string;
    tipo: number;
    documento_numero: string;
    documento_ano: number;
    documento_tipo: number;
    documento_data: string;
    data_efeito_inicio: Date;
    data_efeito_fim: Date;
    gedoc_numero: string;
    login_resp_import: string;
    nome_resp_import: string;
    data_ultima_alteracao_import: string;
    status_import: number;
    codigo_siap_import: string;
    exibir: boolean;
    created_by: number;
    modified_by: number;
    servidor: number;
    publicacao: number;
    publicacao_display: string;
}

class Response extends ListPaginated<ApiAnotacoesPessoaisResponseItem> {}

export async function apiAnotacoesPessoais(payload: Payload) {
    const { data } = await useGet<Response>('anotacoes-pessoais/', payload);
    return data;
}
