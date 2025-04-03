import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    keyword: 'XLS' | 'PDF';
}

class ResponseItem {
    data_inicio_periodo: Date;
    data_fim_periodo: Date;
    data_inicio_abrangencia: Date;
    data_fim_abrangencia: Date;
}

export async function apiRhPvfConfigRequestsVendaPeriodoSubstituicoes(
    payload: Payload
) {
    const { data } = await usePost<ResponseItem>(
        'rh/pvf/config/requests/venda/periodo-substituicoes/',
        payload
    );
    return data;
}
