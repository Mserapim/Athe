import { ListPaginated } from 'api/@base/list-paginated';
import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { DateTime } from 'luxon';

export class ApiPainelControleHistoricoServicosPayload extends ListPayload {
    keyword?: string;
    servico_id?: number;
    executado?: string[];
}

export class ApiPainelControleHistoricoServicosItem {
    id?: number;
    nome?: string;
    comando?: string;
    classcode_path?: string;
    descricao?: string;
    login?: string;
    created_by_unicode?: string;
    modified_by_unicode?: string;
    executado_por_unicode?: string;
    execucao_unicode?: string;
    created_at?: Date;
    modified_at?: Date;
    iniciado_em?: DateTime;
    finalizado_em?: DateTime;
    ssid?: string;
    execucao?: number;
    sucesso?: boolean;
    created_by?: string;
    modified_by?: string;
    servico?: number;
}


export class ApiPainelControleHistoricoServicos extends ListPaginated<ApiPainelControleHistoricoServicosItem> {}

export async function apiPainelControleHistoricoServicos(
    payload: ApiPainelControleHistoricoServicosPayload
) {
    const { data } = await useGet<ApiPainelControleHistoricoServicos>(
        'adm/historico-servicos/',
        payload
    );

    return data;
}
