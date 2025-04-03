import { ListPaginated } from 'api/@base/list-paginated';
import { useGet } from 'api/@base/use-get';

export interface PayloadEstruturaMenus extends ListPaginated<any> {
    palavra_chave?: number;
    servidor_id?:number
}

export class ApiPainelControleControleUsuarioEstrutruraMenusItem {
    nome: string;
    filho: [
        {
            nome: string,
            filho:[
                {
                    nome: string,
                }
            ]
        }
    ]

}

export class ApiPainelControleControleAcessoUsurioEstruturaMenus extends ListPaginated<ApiPainelControleControleUsuarioEstrutruraMenusItem> {}

export async function apiPainelControleControleAcessoUsurioEstruturaMenus(
    payload: PayloadEstruturaMenus
) {
    const { data } = await useGet<ApiPainelControleControleAcessoUsurioEstruturaMenus>(
        'painel-controle/controle-acesso/usuario/estrutura-menus',
        payload
    );

    return data;
}
