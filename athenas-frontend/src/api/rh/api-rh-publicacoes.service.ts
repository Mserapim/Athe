import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    keyword: string;
    page: number;
    per_page: number;
    id?: number;
}

class ResponseItem {
    id: number;
    created_at: Date;
    modified_at: Date;
    publication_state: number;
    indirect: boolean;
    document: string;
    document_read_only: boolean;
    sent_to_publication_at: string;
    confirm_publication_at: string;
    vehicle_page: number;
    tipo: number;
    tipo_display: string;
    numero: string;
    ano: string;
    data_expedicao: string;
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

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhPublicacoes(payload: Payload) {
    const { data } = await useGet<Response>('rh/publicacoes/', payload);
    return data;
}
