import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    id: string | number;
}

export class RhPvfRequestsEnviosRelatorioSemestralTeletrabalhosIdResponse {
    dificuldades_servidores?: string;
    medidas_dirimir_dificuldades_servidores?: string;
    dificuldades_facilidades_gestor?: string;
    medidas_dirimir_dificuldades_gestor?: string;
    resultados_alcancados?: string;
    sugestoes_melhorias?: string;
    plano_servidores?: {
        matricula: string;
        nome: string;
        registros: {
            gedoc: string;
            data_inicio: string;
            data_fim: string;
            envios: string[];
        }[];
    };
}

export async function apiRhPvfRequestsEnviosRelatorioSemestralTeletrabalhosIdService(
    payload: Payload
) {
    const { data } =
        await useGet<RhPvfRequestsEnviosRelatorioSemestralTeletrabalhosIdResponse>(
            '/rh/pvf/requests/envios/relatorio-semestral/teletrabalhos/' +
                payload.id,
            payload
        );
    return data;
}
