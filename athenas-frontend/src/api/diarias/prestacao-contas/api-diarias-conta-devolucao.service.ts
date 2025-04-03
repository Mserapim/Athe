import { useGet } from 'api/@base/use-get';

interface Payload {
}

export class ContaDevolucaoItem {
    baco: string;
    agencia: string;
    conta: string;
    chave_pix:  string;


}

export async function apiDiariasContaDevolucao(
    payload: Payload
) {
    const { data } = await useGet<ContaDevolucaoItem>(
        'diarias/prestacao-contas/conta-devolucao/',
        payload
    );
    return data;
}
