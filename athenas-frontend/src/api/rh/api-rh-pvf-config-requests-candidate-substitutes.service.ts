import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';

interface Payload {
    keyword: string;
}

class PvfRhPvfConfigRequestsCandidateSubstitutesItem {
    pk: number;
    name: string;
    office: string;
}

class Response extends ListPaginated<PvfRhPvfConfigRequestsCandidateSubstitutesItem> {}

export async function apiPvfRhPvfConfigRequestsCandidateSubstitutesService(
    payload: Payload
) {
    const { data } = await useGet<Response>(
        '/rh/pvf/config/requests/candidate-substitutes',
        payload
    );
    return data;
}
