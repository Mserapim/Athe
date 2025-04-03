import { ListPaginated } from 'api/@base/list-paginated';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';

export interface ApiRhPvfRequestsSendingRelatorioSemestralTeletrabalhoPayload {
    page?: number;
}

export class ApiRhPvfRequestsSendingRelatorioSemestralTeletrabalhoItem {
    tipo_ato: string | 'ATO 862/2019';
    dados: {
        matricula: string;
        nome: string;
        registros: {
            gedoc: string;
            data_inicio: string;
            data_fim: string;
            envios: string[];
        }[];
    }[];
}

export class ApiRhPvfRequestsSendingRelatorioSemestralTeletrabalhoResponse extends ListPaginated<ApiRhPvfRequestsSendingRelatorioSemestralTeletrabalhoItem> {}

export async function apiRhPvfRequestsListaRelatorioSemestralteletrabalhos(
    payload: ApiRhPvfRequestsSendingRelatorioSemestralTeletrabalhoPayload
) {
    const { data } =
        await useGet<ApiRhPvfRequestsSendingRelatorioSemestralTeletrabalhoResponse>(
            '/rh/pvf/requests/lista/relatorio-semestral/teletrabalhos/',
            payload
        );
    return data;
}
