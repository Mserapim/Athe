import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    ano_inicial: number;
    ano_final: number;
    matricula: number;
}

export class ApiReportRhPvfFinancialStatementItem {
    uuid: string;
}

export async function apiReportRhPvfFinancialStatement(payload: Payload) {
    const { data } = await usePost<ApiReportRhPvfFinancialStatementItem>(
        '/report/gfp/ficha-financeira/',
        payload
    );
    return data;
}
