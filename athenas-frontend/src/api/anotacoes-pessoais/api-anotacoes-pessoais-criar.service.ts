import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

export interface Payload {
    texto?: string;
    tipo?: number | string;
    documento_numero?: string;
    documento_ano?: number | string;
    documento_tipo?: number | string;
    documento_data?: string;
    data_efeito_inicio?: string;
    data_efeito_fim?: string;
    gedoc_numero?: string;
    login_resp_import?: string;
    nome_resp_import?: string;
    data_ultima_alteracao_import?: string;
    status_import?: number;
    codigo_siap_import?: string;
    exibir?: boolean;
    created_by?: number;
    modified_by?: number;
    servidor?: number;
    publicacao?: number;
}

export class ApiAnotacoesPessoaisCriarResponseItem {
    id: number;
    created_at: string;
    texto: string;
    tipo: number;
    documento_numero: string;
    documento_ano: number;
    documento_tipo: number;
    documento_data: string;
    data_efeito_inicio: string;
    data_efeito_fim: string;
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
}

class Response extends ListPaginated<ApiAnotacoesPessoaisCriarResponseItem> {}

export async function apiAnotacoesPessoaisCriar(payload: Payload) {
    const { data } = await usePost<Response>(
        'anotacoes-pessoais/criar',
        payload
    );
    return data;
}
