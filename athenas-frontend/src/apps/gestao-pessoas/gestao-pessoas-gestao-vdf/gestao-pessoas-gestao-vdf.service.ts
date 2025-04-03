import { Injectable, OnDestroy, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { useDownload } from 'api/@base/use-download';
import { useGedDownload } from 'api/@base/use-ged-download';
import { apiReportRhGestaoVdfService } from 'api/report/api-report-rh-gestao-vdf';
import { apiRhGestaoVdf } from 'api/rh/api-rh-gestao-vdf.service';
import {  ApiVdfGestaoServicePayload } from 'api/vdf/api-vdf-gestao.service';
import { MpmtFormAutocompleteComponentItem } from 'components/mpmt-form-autocomplete/mpmt-form-autocomplete.component';
import { MpmtPaginaListagemAcao, MpmtPaginaListagemColuna, MpmtPaginaListagemOrdenacao } from 'components/mpmt-pagina-listagem/mpmt-pagina-listagem.interface';
import { MpmtPaginaListagemService } from 'components/mpmt-pagina-listagem/mpmt-pagina-listagem.service';
import { formatDate } from 'utils/format-date';

@Injectable()
export class GestaoPessoasGestaoVdfService extends MpmtPaginaListagemService {
 
    filtros = new FormGroup({
        usuarios: new FormControl<MpmtFormAutocompleteComponentItem[]>([], []),
        tipos_solicitacoes: new FormControl<MpmtFormAutocompleteComponentItem[]>([], []),
        categorias: new FormControl<MpmtFormAutocompleteComponentItem[]>([], []),
        tipos_acoes: new FormControl<MpmtFormAutocompleteComponentItem[]>([], []),
        situacoes: new FormControl<MpmtFormAutocompleteComponentItem[]>([], []),
        periodo_tipo: new FormControl<"DT_SOL"|"DT_ACAO">("DT_SOL", []),
        periodo_em: new FormControl<Date[]>([], []),
    });

    constructor() {
        super();
        this.filtros.valueChanges.subscribe(()=>this.recarregarUmaVez())
    }

    protected async obterFiltros(): Promise<{ [key: string]: any }> {
        const { usuarios, tipos_solicitacoes, categorias, tipos_acoes, situacoes, periodo_tipo, periodo_em } = this.filtros.value;

        const filtro: ApiVdfGestaoServicePayload = {
            usuarios: (usuarios||[]).map(x=>x.pk) || undefined,
            tipos_solicitacoes: (tipos_solicitacoes||[]).map(x=>x.value) || undefined,
            categorias: (categorias||[]).map(x=>x.value) || undefined,
            tipos_acoes: (tipos_acoes||[]).map(x=>x.value) || undefined,
            situacoes: (situacoes||[]).map(x=>x.value) || undefined,
            filtrar_por: periodo_tipo == 'DT_SOL' ? 'solicitacao' : 'acao',
        }

        if(periodo_tipo == 'DT_SOL' ){
            filtro.solicitacao_inicio_em  = periodo_em?.length > 0? formatDate(periodo_em[0]): undefined
            filtro.solicitacao_fim_em  = periodo_em?.length > 1? formatDate(periodo_em[1]): undefined 
        }
         
        if(periodo_tipo == 'DT_ACAO' ){
            filtro.acao_inicio_em  = periodo_em?.length > 0? formatDate(periodo_em[0]): undefined
            filtro.acao_fim_em  = periodo_em?.length > 1? formatDate(periodo_em[1]): undefined 
        }

        return filtro
    }

    protected async obterDados(filtros: any) {
        return apiRhGestaoVdf(filtros);
    }

    protected async obterColunas() {
        return <MpmtPaginaListagemColuna[]>[
            {codigo: 'id', titulo: 'Código do Vdf'},
            {codigo: 'data_solicitacao', titulo: 'Data da solicitação', tipo: 'DATA'},
            {codigo: 'tipo_solicitacao', titulo: 'Tipo da solicitação', tipo: 'OBJETO'},
            {codigo: 'servidor', titulo: 'Solicitante'},
            {codigo: 'aprovador', titulo: 'Aprovador'},
            {codigo: 'mes_referencia', titulo: 'Mês de referencia'},
            {codigo: 'solicitante', titulo: 'Periodo aquisitivo'},
            {codigo: 'situacao', titulo: 'Situação', tipo: 'OBJETO'},
        ]
    }

    protected async obterAcoes(): Promise<MpmtPaginaListagemAcao[]> {
        return [
            {
                titulo: 'Visualizar',
                aoClicar: (linha: any) => alert(1),
            },
            {
                visivelSe: (row)=>false,
                titulo: 'Editar',
                aoClicar: (linha: any) => alert(2),
            },
            {
                titulo: 'Apagar',
                aoClicar: (linha: any) => alert(3),
            }
        ]
    }

    protected get downloadCsvSincrono(): boolean {
        return false;
    }

    public async resetar(){
        await this.filtros?.reset()
        await super.resetar()
        this.filtros.patchValue({
            usuarios: [],
            tipos_solicitacoes: [],
            categorias: [],
            tipos_acoes: [],
            situacoes: [],
            periodo_em: [],
            periodo_tipo: 'DT_SOL',
        })
        this.paginacao.page = 1
        this.recarregarUmaVez()
    }

    downloadMensagem = null
    
    async downloadRelatorio(){
        try{
            const filtros = await this.obterFiltros();
            const response = await apiReportRhGestaoVdfService({...filtros})
            this.downloadMensagem = "Processando relatório..."
            const link = await useDownload(response.uuid.toString());
        }catch(e){
            console.log(e);
        }   finally{
            this.downloadMensagem = null
        } 
    }


}
