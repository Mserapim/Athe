import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

export interface Payload {
    id?: string | number;
}

export class ApiAnotacoesPessoaisDetalhesResponse {
    id: number;
    documento_tipo_display: string;
    tipo_display: string;
    data_publicacao: Date;
    data_expedicao_publicacao: Date;
    servidor_nome: string;
    servidor_matricula: string;
    created_at: Date;
    texto: string;
    tipo: number;
    documento_numero: string;
    documento_ano: number;
    documento_tipo: number;
    documento_data: Date;
    data_efeito_inicio: Date;
    data_efeito_fim: Date;
    gedoc_numero: string;
    login_resp_import: string;
    nome_resp_import: string;
    data_ultima_alteracao_import: Date;
    status_import: number;
    codigo_siap_import: string;
    exibir: boolean;
    created_by: number;
    modified_by: number;
    servidor: number;
    publicacao: number;
}

export async function apiAnotacoesPessoaisDetalhes(payload: Payload) {
    const { data } = await useGet<ApiAnotacoesPessoaisDetalhesResponse>(
        'anotacoes-pessoais/detalhes',
        payload
    );
    return data;
}
