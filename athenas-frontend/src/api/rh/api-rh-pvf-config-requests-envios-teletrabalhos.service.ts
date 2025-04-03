import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {}

export class ApiRhPvfEnviosTeletrabalhosResponseItem {
    id: number;
    tipo_solicitacao: string;
    referencia: string;
    status: string;
    inicio_plano: string;
    fim_plano: string;
    date: Date;
}

class Response extends ListPaginated<ApiRhPvfEnviosTeletrabalhosResponseItem> {}

export async function apiRhPvfEnviosTeletabalho(payload: Payload) {
    const { data } = await useGet<Response>(
        '/rh/pvf/requests/envios/teletrabalhos',
        payload
    );
    return data;
}
