import { usePost } from 'api/@base/use-post';

interface Payload {
    beneficiario: number;
    gedoc: string;
    quantidadeDeferida?: number;
    acaoDeferimento: boolean;
    anexos: any[];
}

export class ApiBenecificarioAnaliseDefinExcedentes {
    beneficiario: number;
}

export async function apiBenecificarioAnaliseDefinExcedentes(
    payload: Payload
) {
    const { data } = await usePost<any>(
        'diarias/beneficiario/analise-defin-excedente/',
        payload
    );
    return data.data;
}
