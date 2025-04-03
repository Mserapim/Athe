import { ListPayload } from 'api/@base/list-payload';
import { useGet } from 'api/@base/use-get';
import { usePost } from 'api/@base/use-post';
import { ListPaginated } from 'api/@base/list-paginated';

interface Payload extends ListPayload {
    id?: number;
    palavra_chave?: number;
    situacao?: string;
}

interface Data {
    id?: number;
    place: string;
    prosecution: string;
    network: string;
}

interface Detalhe {
    id: number;
}

export class ApiPainelControleControleAcessoConfigPontoItem {
    id: number;
    place: string;
    prosecution: string;
    network: string;
}

export class ApiPainelControleControleAcessoConfigPonto extends ListPaginated<ApiPainelControleControleAcessoConfigPontoItem> {}

export async function apiPainelControlConfigPonto(payload: Payload) {
    const { data } = await useGet<ApiPainelControleControleAcessoConfigPonto>(
        'painel-controle/configuracoes/configuracoes-de-ponto/',
        payload
    );

    return data;
}


export async function apiPainelControleControleConfigPontoCriar(
    payload: Data
) {
    const { data } = await usePost<ApiPainelControleControleAcessoConfigPontoItem>(
        'painel-controle/configuracoes/configuracao-de-ponto/criar/',
        payload
    );

    return data;
}

export async function apiPainelControleControleConfigPontoEditar(
    payload: Data
) {
    const { data } = await usePost<ApiPainelControleControleAcessoConfigPontoItem>(
        'painel-controle/configuracoes/configuracao-de-ponto/editar/',
        payload
    );

    return data;
}

export async function apiPainelControleControleConfigPontoApagar(
    payload: Detalhe
) {
    const { data } = await usePost<ApiPainelControleControleAcessoConfigPontoItem>(
        'painel-controle/configuracoes/configuracao-de-ponto/apagar/',
        payload
    );

    return data;
}


export async function apiPainelControleControleConfigPontoDetail(
    payload: Detalhe
) {
    const { data } = await useGet<ApiPainelControleControleAcessoConfigPontoItem>(
        'painel-controle/configuracoes/configuracao-de-ponto/',
        payload
    );

    return data;
}
