import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { AcquisitionPeriodsStatusEnum } from 'enums/acquisition-periods-status.enum';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

interface Payload extends ListPayload {
    keyword: string;
    page: number;
    per_page: number;
}

class ResponseItem {
    cod: string;
    descricao: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhCategoriaFuncional(payload: Payload) {
    const { data } = await useGet<Response>('rh/tipo-posses/', payload);
    return data;
}
