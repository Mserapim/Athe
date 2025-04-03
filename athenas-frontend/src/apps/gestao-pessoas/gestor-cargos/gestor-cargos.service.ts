import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { apiGestorCargos, ApiGestorCargosPayload } from 'api/gestao/api-gestao-pessoas-gestor-cargos.service';
import { MpmtFormAutocompleteComponentItem } from 'components/mpmt-form-autocomplete/mpmt-form-autocomplete.component';
import { MpmtPaginaListagemColuna } from 'components/mpmt-pagina-listagem/mpmt-pagina-listagem.interface';
import { MpmtPaginaListagemService } from 'components/mpmt-pagina-listagem/mpmt-pagina-listagem.service';

@Injectable()
export class GestorCargosService extends MpmtPaginaListagemService {
    filtros = new FormGroup({
        keyword: new FormControl<string>('', []),
        tipo_lei_cargos: new FormControl<MpmtFormAutocompleteComponentItem[]>([], []),
    });

    constructor(public dialog: MatDialog) {
        super();
        this.filtros.valueChanges.subscribe(()=>this.recarregarUmaVez());
    }

    public async obterDados(filtros: any) {
        const response = await apiGestorCargos(filtros);

        return response;
    }

    protected async obterFiltros(): Promise<{ [key: string]: any }> {
        const { keyword, tipo_lei_cargos } = this.filtros.value;
        
        const filtro: ApiGestorCargosPayload = {
            keyword: keyword || undefined,
            tipo_lei_cargos: (tipo_lei_cargos || []).map(x => x.valor) || undefined,
        };
    
        return filtro;
    }

    protected async obterColunas() {
        return <MpmtPaginaListagemColuna[]>[
            {
                codigo: 'id',
                titulo: 'Chave',
                visivel: false,
            },
            {
                codigo: 'ativo',
                titulo: 'Ativo',
                tipo: 'BOLEANO_ICONE',
            },            
            {
                codigo: 'descricao',
                titulo: 'Descrição',
            },
            {
                codigo: 'tipo_lei_cargo',
                titulo: 'Tipo Lei Cargo',
                tipo: 'OBJETO',
            },
            {
                codigo: 'indicativo',
                titulo: 'Indicativo',
                tipo: 'OBJETO',
            },
            {
                codigo: 'codigo',
                titulo: 'Código',
            },
            {
                codigo: 'qtd_vagas',
                titulo: 'Qtd. Vagas',
            },
            {
                codigo: 'chefia',
                titulo: 'Chefia',
                transformarValor: (linha: any) => {
                    return linha.chefia ? 'SIM' : '-';
                } 
            },            
            {
                codigo: 'substituivel',
                titulo: 'Substituível',
                transformarValor: (linha: any) => {
                    return linha.substituivel ? 'SIM' : '-';
                } 
            },            
            {
                codigo: 'acumulacao',
                titulo: 'Acumulação',
                tipo: 'OBJETO',
            },
            {
                codigo: 'nivel_escolaridade',
                titulo: 'Escolaridade',
                tipo: 'OBJETO',
            },            
            {
                codigo: 'inicio_vigencia',
                titulo: 'Início Vigência',
                tipo: 'DATA',
            },   
            {
                codigo: 'inicio_vigencia',
                titulo: 'Fim Vigência',
                tipo: 'DATA',
                visivel: false,
            },            
            {
                codigo: 'poder',
                titulo: 'Poder',
                tipo: 'OBJETO',
                visivel: false,
            },
            {
                codigo: 'nome',
                titulo: 'Nome',
                visivel: false,
            },
            {
                codigo: 'lotacao_responsavel',
                titulo: 'Responsável pela lotação',
                tipo: 'OBJETO',
                visivel: false,
            },
            {
                codigo: 'publicacao',
                titulo: 'Publicação',
                tipo: 'OBJETO',
                visivel: false,
            },
            {
                codigo: 'unidade_administrativa',
                titulo: 'Órgão',
                tipo: 'OBJETO',
                visivel: false,
            },
            {
                codigo: 'cargo_arquimedes',
                titulo: 'Cargo Arquimedes',
                visivel: false,
            },
            {
                codigo: 'peso_ordenacao',
                titulo: 'Peso Ordenação',
                visivel: false,
            },
        ]
    }

}

