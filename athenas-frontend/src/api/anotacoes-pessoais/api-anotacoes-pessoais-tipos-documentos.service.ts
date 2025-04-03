import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { ListPayload } from 'api/@base/list-payload';

export interface Payload extends ListPayload {
    keyword?: string;
}

export class ApiAnotacoesPessoaisTiposDocumentosResponseItem {
    value: number;
    label: string;
}

class Response extends ListPaginated<ApiAnotacoesPessoaisTiposDocumentosResponseItem> {}

export async function apiAnotacoesPessoaisTiposDocumentos(payload: Payload) {
    const { data } = await useGet<Response>(
        'anotacoes-pessoais/tipos-documentos',
        payload
    );
    return data;
}
