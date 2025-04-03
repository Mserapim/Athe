import {ListPayload} from "../@base/list-payload";
import {DateTime} from "luxon";
import {ListPaginated} from "../@base/list-paginated";
import {useGet} from "../@base/use-get";

interface Payload extends ListPayload {
    keyword: string;
    'categoria[]': number[]
    'status[]': number[]
    'orientacao_cpf[]': number[]
    'orientacao_nis[]': number[]
}

class ResponseItem {
    id: number;
    nome: string;
    cpf: string;
    nis: string;
    data_nascimento: string;
    servidor: string;
    cod_cpf_inv: number;
    cod_nis_inv: number;
    cod_nome_inv: number;
    cod_dn_inv: number;
    cod_cnis_nis: number;
    cod_cnis_dn: number;
    cod_cnis_obito: number;
    cod_cnis_cpf: number;
    cod_cnis_cpf_nao_inf: number;
    cod_cpf_nao_consta: number;
    cod_cpf_nulo: number;
    cod_cpf_cancelado: number;
    cod_cpf_suspenso: number;
    cod_cpf_dn: number;
    cod_cpf_nome: string;
    cod_orientacao_cpf: number;
    cod_orientacao_nis: number;
    ultima_qualificacao: string;
    ultima_qualificacao_por: string;
    ultima_mofificacao: string;
    ultima_mofificacao_por: string;
    tipo_pessoa: number;
    tipo_pessoa_display: string;
    qualificado: boolean;
    status: number;
    status_display: string;
    tipo_ultima_qualificacao: number;
    tipo_ultima_qualificacao_display: string;
    info: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiESocialListarQualificacaoCadastral(payload: Payload) {
    const { data } = await useGet<Response>('esocial/qualificacoes-cadastrais/', payload);
    return data;
}
