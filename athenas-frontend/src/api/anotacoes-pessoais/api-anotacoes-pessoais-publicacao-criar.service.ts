import { usePost } from 'api/@base/use-post';

export interface Payload {
    publication_state: number;
    indirect: boolean;
    document: string;
    document_read_only: boolean;
    sent_to_publication_at: Date;
    confirm_publication_at: Date;
    vehicle_page: number;
    tipo: number;
    numero: string;
    ano: string;
    data_expedicao: Date;
    lei_autorizativa: boolean;
    veiculo_publicacao: number;
    numero_publicacao: string;
    data_publicacao: Date;
    data_vigencia: Date;
    observacao: string;
    interno: boolean;
    interessado_nome: string;
    cache_unicode: string;
    import_siap: boolean;
    created_by: number;
    modified_by: number;
    sent_to_publication_by: number;
    confirm_publication_by: number;
    origem: number;
    arquivo: number;
}

export class ApiAnotacoesPessoaisPublicacaoCriarResponse {
    publication_state: number;
    indirect: boolean;
    document: string;
    document_read_only: boolean;
    sent_to_publication_at: Date;
    confirm_publication_at: Date;
    vehicle_page: number;
    tipo: number;
    numero: string;
    ano: string;
    data_expedicao: Date;
    lei_autorizativa: boolean;
    veiculo_publicacao: number;
    numero_publicacao: string;
    data_publicacao: Date;
    data_vigencia: Date;
    observacao: string;
    interno: boolean;
    interessado_nome: string;
    cache_unicode: string;
    import_siap: boolean;
    created_by: number;
    modified_by: number;
    sent_to_publication_by: number;
    confirm_publication_by: number;
    origem: number;
    arquivo: number;
}

export async function apiAnotacoesPessoaisPublicacaoCriar(payload: Payload) {
    const { data } = await usePost<ApiAnotacoesPessoaisPublicacaoCriarResponse>(
        'anotacoes-pessoais/criar',
        payload
    );
    return data;
}
