import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    id: number;
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

class Response {
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

export async function apiRhPublicacaoEditar(payload: Payload) {
    const { data } = await usePost<Response>('rh/publicacao/editar', payload);
    return data;
}
