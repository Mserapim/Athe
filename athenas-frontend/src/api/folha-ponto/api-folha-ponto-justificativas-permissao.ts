import { useGet } from 'api/@base/use-get';

interface Payload {}

export class ApiFolhaPontoJustificativasPermissao {
    pode_adicionar_justificativa: boolean;
}

export async function apiFolhaPontoJustificativasPermissao(payload: Payload) {
    const { data } = await useGet<ApiFolhaPontoJustificativasPermissao>(
        'folha-ponto/justificativas/permissao/',
        payload
    );

    return data;
}
