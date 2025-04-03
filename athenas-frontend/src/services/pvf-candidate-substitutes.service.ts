import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

interface Payload {
    page: number;
}

class ResponseItem {
    pk: number;
    name: string;
    office: string;
}

class Response extends ListPaginated<ResponseItem> {}

/** @deprecated */
export async function pvfCandidatSubstitutesService(payload: Payload) {
    const { data } = await useGet<Response>(
        '/rh/pvf/candidate_substitutes',
        payload
    );
    return data;
}
