import { usePost } from 'api/@base/use-post';


interface Payload {
    id: number;
    ordem?: number;
    etapa?: number;
    situacao?: number;
    notificar_solicitante?: boolean;
    notificar_emails?: string[];
    condicionais?: Condicional[];
    deferir_todos_beneficiarios?: boolean;
    calcular?: boolean;
    link_informacao?: string;
}

export class ApiDiariasConfigFluxoEditar {
    id: number;
    ordem: number;
    etapa: number;
    situacao: number;
    notificar_solicitante: boolean;
    condicionais?: Condicional[];
    deferir_todos_beneficiarios?: boolean;
    calcular?: boolean;
    link_informacao?: string;
}

interface Condicional {
    condicao: number; 
    operador?: string;
}

export async function apiDiariasConfigFluxoEditar(
    payload: Payload
) {
    const { data } = 
        await usePost<ApiDiariasConfigFluxoEditar>(
        'diarias/config/fluxo/editar/',
        payload
    );

    return data;
}
