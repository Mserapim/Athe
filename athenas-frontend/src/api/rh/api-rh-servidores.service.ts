import { useGet } from 'api/@base/use-get';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload {
    palavra_chave?: string;
    page?: number;
    per_page: number;
    situacao?: boolean;
    tipo_posse?: string[];
    tipo_posse_exclude?: string[];
    tipo_dados_pessoais?: string;
    tipo_dados_servidor?: string;
}

class ResponseItem {
    pk: number;
    nome: string;
    matricula: number;
    tipo_posse: string;
    ativo: boolean;
    data_posse: Date;
    unicode: string;
    cpf?: string;
    sexo?: string;
    sangue?: string;
    email_pessoal?: string;
    email_institucional?: string;
    chefe_imediato?: string;
    lotacao?: number;
    cargo?: string;
}

class Response extends ListPaginated<ResponseItem> {}

export async function apiRhSevidoresService(payload: Payload) {
    const { data } = await useGet<Response>('rh/servidores', payload);
    return data;
}
