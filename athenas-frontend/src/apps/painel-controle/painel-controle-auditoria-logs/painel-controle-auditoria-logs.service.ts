import { Injectable } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { apiAuditoriaLogs, ApiAuditoriaLogsPayload } from 'api/painel-controle/api-painel-controle-auditoria-logs.service';
import { MpmtFormAutocompleteComponentItem } from 'components/mpmt-form-autocomplete/mpmt-form-autocomplete.component';
import { MpmtPaginaListagemAcao, MpmtPaginaListagemColuna } from 'components/mpmt-pagina-listagem/mpmt-pagina-listagem.interface';
import { MpmtPaginaListagemService } from 'components/mpmt-pagina-listagem/mpmt-pagina-listagem.service';
import { formatDate } from 'utils/format-date';
import { AuditoriaLogsModalComponent } from './modal-auditoria-logs/modal-auditoria-logs.component';

@Injectable()
export class AuditoriaLogsService extends MpmtPaginaListagemService {
    filtros = new FormGroup({
        keyword: new FormControl<string>('', []),
        modelos: new FormControl<MpmtFormAutocompleteComponentItem[]>([], []),
        acoes: new FormControl<MpmtFormAutocompleteComponentItem[]>([], []),
        periodo_em: new FormControl<Date[]>([], []),
    });

    constructor(public dialog: MatDialog) {
        super();
        this.filtros.valueChanges.subscribe(()=>this.recarregarUmaVez());
    }

    public async obterDados(filtros: any) {
        const response = await apiAuditoriaLogs(filtros);
    
        response.results = response.results.map(item => ({
            ...item,
            modelo_id: item.modelo?.id ?? null, 
        }));
    
        return response;
    }

    protected async obterFiltros(): Promise<{ [key: string]: any }> {
        const { keyword, modelos, acoes, periodo_em } = this.filtros.value;
        
        const filtro: ApiAuditoriaLogsPayload = {
            keyword: keyword || undefined,
            modelos: (modelos || []).map(x => x.value) || undefined,
            acoes: (acoes || []).map(x => x.value) || undefined,
        };

        if (periodo_em?.length > 0) {
            filtro.log_inicio_em = periodo_em[0] ? formatDate(periodo_em[0]) : undefined;
            filtro.log_fim_em = periodo_em[1] ? formatDate(periodo_em[1]) : undefined;
        };

        return filtro;
    }

    protected async obterColunas() {
        return <MpmtPaginaListagemColuna[]>[
            {
                codigo: 'objeto_id',
                titulo: 'Id do registro',
            },
            {
                codigo: 'id',
                titulo: 'Id',
                visivel: false,
            },            
            {
                codigo: 'modelo_id',
                titulo: 'Id do modelo',
                visivel: false,
            },
            {
                codigo: 'modelo',
                titulo: 'Modelo',
                tipo: 'OBJETO',
            },
            {
                codigo: 'acao',
                titulo: 'Ação',
                tipo: 'OBJETO',
            },
            {
                codigo: 'usuario',
                titulo: 'Usuário',
            },
            {
                codigo: 'data',
                titulo: 'Data',
                tipo: 'DATA_HORA',
            },
            {
                codigo: 'endereco_ip',
                titulo: 'Endereço IP',
            },
        ]
    }

    protected async obterAcoes(): Promise<MpmtPaginaListagemAcao[]> {
        return [
            {
                titulo: 'Visualizar',
                icone: 'visibility',
                requerPermissao: 'ver',
                aoClicar: (linha: any) => this.verLog(linha),
            },
        ]
    }

    protected verLog(linha) {
        this.dialog.open(AuditoriaLogsModalComponent, {
            data: {
                linha: linha,
            },
        });
    }
}

