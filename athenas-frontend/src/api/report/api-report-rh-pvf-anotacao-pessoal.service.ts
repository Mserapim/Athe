import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

export interface Payload {
    tipos_anotacao?: number[];
}

export class ApiReportRhPvfAnotacaoPessoalResponseItem {
    message: string;
    success: boolean;
    uuid: string;
}

export async function apiReportRhPvfAnotacaoPessoalService(payload: Payload) {
    const { data } = await usePost<ApiReportRhPvfAnotacaoPessoalResponseItem>(
        '/report/rh/pvf/anotacao-pessoal/',
        payload
    );
    return data;
}
