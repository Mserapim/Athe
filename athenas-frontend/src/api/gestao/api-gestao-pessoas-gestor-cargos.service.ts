import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';
import { DateTime } from 'luxon';

export interface ApiGestorCargosPayload extends ListPayload {
    keyword?: string;
    tipo_lei_cargos?: string[] | string;
}

interface ResponseItem {
    id: number;
    descricao: string;
    criado_em: DateTime;
    modificado_em: DateTime;
    nome: string;
    indicativo: {
        valor: string;
        display: string;
    };
    tipo_lei_cargo: {
        valor: string;
        display: string;
    };
    codigo: number;
    qtd_vagas: number;
    nivel_escolaridade: {
        valor: string;
        display: string;
    };
    inicio_vigencia: Date;
    fim_vigencia: Date;
    ativo: boolean;
    poder: {
        valor: number;
        display: string;
    };
    chefia: boolean;
    substituivel: boolean;
    cargo_arquimedes: number;
    peso_ordenacao: number;
    acumulacao: {
        valor: number;
        display: string;
    };
    code_tce: number;
    criado_por: {
        id: number;
        display: string;
    };
    modificado_por: {
        id: number;
        display: string;
    };
    lotacao_responsavel: {
        id: number;
        display: string;
    };
    unidade_administrativa: {
        id: number;
        display: string;
    };
    publicacao: {
        id: number;
        display: string;
    };
    publicacao_alteracao: {
        id: number;
        display: string;
    };
    publicacao_extincao: {
        id: number;
        display: string;
    };
    configs: [
        {
            id: number;
            ativo: boolean;
            nome: string;
            codigo: number;
            designa_exercicio: boolean;
            chefia: boolean;
            substituivel: boolean;
            remunerado: boolean;
            acumulacao: {
                valor: number;
                display: string;
            };
            qtd_vagas: number;
            cbo: {
                id: number;
                display: string;
            };
            nivel_escolaridade: {
                valor: number;
                display: string;
            };
            carga_horaria: number;
            tipo_carga_horaria: {
                valor: number;
                display: string;
            };
            inicio_vigencia: Date;
            fim_vigencia: Date;
        }
    ];
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiGestorCargos(payload: ApiGestorCargosPayload) {
    const { data } = await useGet<Response>('rh/cargos/', payload);
    return data;
}
