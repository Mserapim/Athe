import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    id_beneficiario: number;
    notificar?: boolean;

}

class ResponseItem {
    uuid: string;
    error?: any;
    message: string;
}

export async function apiReportDiariasOsConsolidada(payload: Payload) {
    const { data } = await usePost<ResponseItem>(
        'report/diarias/os-consolidada/',
        payload
    );
    return data;
}
