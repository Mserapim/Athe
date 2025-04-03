import { usePost } from 'api/@base/use-post';

interface Payload {
    beneficiario: number;
    cienciaChefe: boolean;
}

export class ApiBenecificarioCienciaChefeImediato {
    beneficiario: number;
    cienciaChefe: boolean;
}

export async function apiBenecificarioCienciaChefeImediato(
    payload: Payload
) {
    const { data } = await usePost<any>(
        'diarias/beneficiario/ciencia-chefe-imediato/',
        payload
    );
    return data.data;
}
