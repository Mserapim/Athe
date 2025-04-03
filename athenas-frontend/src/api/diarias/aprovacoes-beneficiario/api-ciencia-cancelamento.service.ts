import { usePost } from 'api/@base/use-post';

interface Payload {
    beneficiarios: number[];
}

export async function apiCienciaCancelamentoDiarias(
    payload: Payload
) {
    const { data } = await usePost<any>(
        'diarias/beneficiarios/ciencia-cancelamento/',
        payload
    );
    return data.data;
}
