import { useGet } from 'api/@base/use-get';
import { ListPaginated } from '../@base/list-paginated';

interface Payload {
    servidor_id?: number;
}

export class ApiPainelControleControleAcessoModulosUsuario {
    pk: number;
    nome?: string;
    ordem?: number;
    situacao: 'ATIVO' | string;
    codigo?: string;
    sigla?: string;
    icone?: string;
}

export async function apiPainelControleControleAcessoModulosUsuario(
    payload: Payload
) {
    const { data } = await useGet<
        ListPaginated<ApiPainelControleControleAcessoModulosUsuario>
    >('/painel-controle/controle-acesso/modulos/usuario/', payload);

    return data;
}
