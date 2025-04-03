import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';
import { DateTime } from 'luxon';

interface Payload extends ListPayload {
    keyword: string;
}

class ResponseItem {
    pk: number;
    nome: string;
    matricula: number;
    cpf: string;
    ordem_antiguidade: number;
    data_inicio_instancia: Date;
    data_inicio_carreira: Date;
    tempo_afastamento_formatado: string;
    total_instancia_formatado: string;
    efetivo_exercicio_formatado: string;
    total_carreira_formatado: string;
    get_origem_display: string;
    get_tipo_cargo_display: string;
    posicao_concurso: number;
    modified_at: DateTime;
    
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhListaAntiguidades(payload: Payload) {
    const { data } = await useGet<Response>('rh/antiguidades/lista/', payload);
    console.log(data)
    return data;
}
