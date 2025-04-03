import { useGet } from 'api/@base/use-get';

interface Payload {
    id?: number;
}

export class ApiDiariasConfigFluxo {
    id: number;
    ordem: number;
    etapa: number;
    situacao: number;
    notificar_solicitante: boolean;
    situacao_display: string;
    etapa_display: string;
    condicionais: Condicionais[];
    condicionais_descricao: string;
    criado_por_username: string;
    created_at: Date;
    modificado_por_username: string;
    modified_at: Date;
    notificar_emails: string[];
    deferir_todos_beneficiarios?: boolean;
    calcular?: boolean;
    link_informacao?: string;
}

export interface Condicionais {
    id: number;
    condicionais: string[]; 
    descricao: string[];
}

export async function apiDiariasConfigFluxo(payload: Payload) {
    const { data } = await useGet<ApiDiariasConfigFluxo>(
        'diarias/config/fluxo/',
        payload
    );

    return data;
}
