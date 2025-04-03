import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

export interface Payload extends ListPayload {
    id: number;
}

export class ApiDiariasBeneficiariosResponseItem {
    id:number;
    servidor_unicode: string; 
    servidor_nome: string; 
    servidor_matricula: string; 
    servidor_cpf: string; 
    categoria_funcional: string;
    lotacao: string;
    conta_bancaria_unicode: string;
    conta_bancaria_tipo: string;
    codigo_os: string;
    codigo_os_viagem_original: string;
    codigo_os_excedente: string;
    total_distancia_destinos: number;
    conta_bancaria_pgto: number;
    fluxo: number;
    fluxo_unicode: string;
    etapa_fluxo: number;
    qtd_total_diarias: number;
    qtd_total_diarias_deferido: number;
    pode_editar_valor_deferido: boolean;
    reanalise: boolean;
    acomp_autoridade_deferimento: boolean;
    acomp_autoridade: boolean;
}


class Response extends ListPaginated<ApiDiariasBeneficiariosResponseItem> {}

export async function apiDiariasBeneficiario(
    payload: Payload
) {
    const { data } = await useGet<ApiDiariasBeneficiariosResponseItem>(
        'diarias/minhas-diarias/beneficiario/',
        payload
    );
    return data;
}