import {useGet} from "../@base/use-get";


class ResponseItem {
    certificado_a1_id: number;
    certificado_cas_id: number;
    nome_certificado_a1: string;
    nome_certificado_cas: string;
}

class Response extends ResponseItem {}

export async function apiESocialBuscarCertificadoAtual() {
    const { data } = await useGet<Response>('esocial/configuracao/certificado-digital/');
    return data;
}
