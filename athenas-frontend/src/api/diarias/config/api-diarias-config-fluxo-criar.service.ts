import { usePost } from 'api/@base/use-post';


interface Payload {
    ordem: number;
    etapa: number;
    situacao: number;
    notificar_solicitante: boolean;
    condicionais?: Condicional[];
    deferir_todos_beneficiarios?: boolean;
    calcular?: boolean;
    link_informacao?: string;
}

export class ApiDiariasConfigFluxoCriar {
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

export async function apiDiariasConfigFluxoCriar(
    payload: Payload
) {
    const { data } = 
        await usePost<ApiDiariasConfigFluxoCriar>(
        'diarias/config/fluxo/criar/',
        payload
    );

    return data;
}
