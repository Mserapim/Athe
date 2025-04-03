import { usePost } from 'api/@base/use-post';

interface Payload {
    servidor: number;
    tipos_documento?: number[];
    tipos_anotacao?: number[];
    notificar: boolean;
}

export class ApiReportAnotacaoPessoalAnotacoesPessoaisResponseItem {
    message: string;
    success: boolean;
    uuid: string;
}

export async function apiReportAnotacaoPessoalAnotacoesPessoaisService(payload: Payload) {
    const { data } = await usePost<ApiReportAnotacaoPessoalAnotacoesPessoaisResponseItem>(
        '/report/anotacao-pessoal/anotacoes-pessoais/',
        payload
    );
    return data;
}
