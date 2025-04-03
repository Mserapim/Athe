import { useGet } from 'api/@base/use-get';

export interface ApiDetalheSolicitacaoFolgaPayload {
    id: number;
}

export class ApiVdfSolicitacaoFolgaResponse {
    data_inicio: string;
    data_fim: Date;
    tipo_folga: string;
    dias:number;
    anexo: number;
    tipo_folga_display:string;
}

export async function apiVdfDetalhesSolicitacaoFolga(
    payload: ApiDetalheSolicitacaoFolgaPayload
) {
    const { data } =
        await useGet<ApiVdfSolicitacaoFolgaResponse>(
            '/vdf/solicitacao-folga/',
            payload
        );
    return data;
}
