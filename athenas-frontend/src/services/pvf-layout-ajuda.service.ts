import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

export class Payload {
    sigla: string;
}


export class PvfAjudaResponseItem {
    link_de_ajuda: string;
}

class Response extends PvfAjudaResponseItem {}

export async function pvfAjudaService(payload: Payload) {
    const { data } = await useGet<Response>('painel-controle/controle-acesso/menu/ajuda/', payload);
    return data;
}
