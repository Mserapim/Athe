import { usePost } from 'api/@base/use-post';

interface Payload {
    viagem: number;
}

export class ApiReceberBeneficiarios {
    viagem: number;
}

export async function apiReceberBeneficiarios(
    payload: Payload
) {
    const { data } = await usePost<any>(
        'diarias/viagem/receber-beneficiarios/',
        payload
    );
    return data.data;
}
