import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    ano?: number;
    fim?: string;
    inicio?: string;
    keyword?: string;
    mes?: number;
    servidor_id?: number;
    tipos_dia?: number[];
}

export class ApiFolhaPontoMarcacoesItem {
    afastamento_pendente: string;
    carga_horaria: string;
    data: string;
    dia: string;
    editavel: boolean;
    marcacoes: {
        id: number;
        marcacao_hora: string;
        marcacao_valida: boolean;
        editado_por: string;
        editado_por_nome: string;
    }[];
    saldo_dia: string;
    tipo: string;
    tipo_texto: string;
    total_dia: string;
}

export class ApiFolhaPontoMarcacoes extends ListPaginated<ApiFolhaPontoMarcacoesItem> {}

export async function apiFolhaPontoMarcacoes(payload: Payload) {
    return await useGet<ApiFolhaPontoMarcacoes>(
        'folha-ponto/marcacoes/',
        payload
    );
}
