import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { usePost } from 'api/@base/use-post';

interface Payload {
    dificuldades_servidores: string;
    medidas_dirimir_dificuldades_servidores: string;
    dificuldades_facilidades_gestor: string;
    medidas_dirimir_dificuldades_gestor: string;
    resultados_alcancados: string;
    sugestoes_melhorias: string;
}

class Response {
    dificuldades_servidores: string;
    medidas_dirimir_dificuldades_servidores: string;
    dificuldades_facilidades_gestor: string;
    medidas_dirimir_dificuldades_gestor: string;
    resultados_alcancados: string;
    sugestoes_melhorias: string;
}

export async function apiRhPvfRequestsEnviosRelatorioSemestralTeletrabalhosService(
    payload: Payload
) {
    const { data } = await usePost<Response>(
        '/rh/pvf/requests/envios/relatorio-semestral/teletrabalhos/',
        payload
    );
    return data;
}
