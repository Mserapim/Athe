import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

interface Payload {
    page: number;
}

class ResponseItem {
    header: string;
    title: string;
    action: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function pvfEmployePendingsService(payload: Payload) {
    const { data } = await useGet<Response>(
        '/rh/pvf/employe_pendings',
        payload
    );
    return data;
}
