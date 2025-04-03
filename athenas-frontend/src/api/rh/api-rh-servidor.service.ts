import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    id: number;
    tipo_dados_pessoais?: string;
    tipo_dados_servidor?: string;
}

export class ResponseItem {
    pk: number;
    nome: string;
    matricula: number;
    tipo_posse: string;
    ativo:boolean;
    data_posse: Date;
    unicode: string;
    cpf?: string;
    sexo?: string;
    sangue?: string;
    email_pessoal?: string;
    email_institucional?: string;
    chefe_imediato?: string;
    lotacao?: number;
    lotacao_display?: string;
    cargo?: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhSevidorService(payload: Payload) {
    const { data } = await useGet<Response>('rh/servidor/', payload);
    return data;
}
