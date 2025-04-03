import { ListPaginated } from 'api/@base/list-paginated';
import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { DateTime } from 'luxon';

export class ApiPainelControleServicosPayload extends ListPayload {
    name?: string;
    command?: string;
    description?: string;
}

export class ApiPainelControleServicosItem {
    id?: number;
    name?: string;
    command?: string;
    description?: string;
    classcode?: string;
    created_at?: Date;
    modified_at?: Date;
    created_by?: string;
    modified_by?: string;
    classcode_path?: string;
    created_by_unicode?: string;
    modified_by_unicode?: string;
    executado_em?: DateTime;
    executado_por_unicode?: string;
    executado?: boolean;
    em_execucao?: boolean;
    status_execucao?: string;
}

export class ApiPainelControleServicos extends ListPaginated<ApiPainelControleServicosItem> {}

export async function apiPainelControleServicos(
    payload: ApiPainelControleServicosPayload
) {
    const { data } = await useGet<ApiPainelControleServicos>(
        'adm/servicos/',
        payload
    );

    return data;
}
