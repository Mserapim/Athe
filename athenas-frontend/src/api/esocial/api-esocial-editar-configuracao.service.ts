import { usePost } from 'api/@base/use-post';

export interface Payload {
    id: number,
    ambiente: number;
    layout_versao: string;
    webservice_envio: string;
    webservice_consulta: string;
    inicio_vigencia: string;
    fim_vigencia: string;
    data_corte_s2231: string;
    orgao_empregador_id: number;
    tabela_iniciais: string;
    nao_periodicos: string;
    periodicos: string;
    sst: string;
    envio_fila: boolean;
    servidores_gerados_ids: number[]
    eventos_gerados_ids: number[]
    responsavel_id: number;
    responsavel_sowfware_house_id: number;
    nome_schema_envio: string;
    nome_schema_consulta: string;
    url_consulta: string;
    url_envio: string;

    //campos não utilizados mas que seram mandados como []
    eventos_nao_enviados_ids: number[];
    servidores_nao_gerados_ids: number[];
    beneficiarios_gerados_ids: number[];
    beneficiarios_nao_gerados_ids: number[];
}

export async function apiESocialEditarConfiguracao(
    payload: Payload
) {
    const { data } = await usePost<any>(
        'esocial/configuracao/editar/',
        payload
    );
    return data;
}
