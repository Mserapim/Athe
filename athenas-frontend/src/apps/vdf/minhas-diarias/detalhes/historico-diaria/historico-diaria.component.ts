import { Component, Inject, Optional } from "@angular/core";
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from "@angular/material/dialog";
import { MatSnackBar } from "@angular/material/snack-bar";
import { apiDiariasDetalheHistorico } from "api/diarias/detalhe/api-diarias-viagem-historico.service";
import { VerDiariaService } from "apps/diarias/gestao/viagem/ver-diaria-aprovador/ver-diaria-aprovador.service";
import { MpmtFormularioComponent } from "components/mpmt-formulario/mpmt-formulario.component";
import { DiariaHistoricoDetalheComponent } from "./historico-diaria-anexos-informacoes/historico-diaria-anexos-informacoes.component";

class HistoricoDiariaComponentData {
    id: number;
}

@Component({
    selector: 'historico-diaria',
    templateUrl: 'historico-diaria.component.html',
    standalone: false
})
export class HistoricoDiariaComponent extends MpmtFormularioComponent<HistoricoDiariaComponentData>{
    historico: any = [];

    constructor(
        @Inject(MAT_DIALOG_DATA) protected data: HistoricoDiariaComponentData,
        @Optional() protected dialogRef: MatDialogRef<HistoricoDiariaComponentData>,
        protected snackBar: MatSnackBar,
        private verDiariaService: VerDiariaService,
        public dialog: MatDialog,
    ) {
        super(data, snackBar, dialogRef);
    }

    ngOnInit() {
        super.ngOnInit();
        this.carregarHistoricoViagem();
    }

    async carregarHistoricoViagem() {
        const id = this.data && this.data.id ? this.data.id : this.verDiariaService.viagemId;
        if (id != null) {
            try {
                const historico = await apiDiariasDetalheHistorico({ viagem_id: id });
                this.historico = historico.results.map(item => ({
                    ...item,
                    acao_por: item.ação_por
                }));
            } catch (e: any) {
                const detalheErro = e?.response?.data?.message || 'Não foi possível carregar os dados.';
                this.exibirMensagem('Erro', detalheErro);
            }
        }
    }

    protected exibirMensagem(titulo: string, texto: string) {
        this.snackBar.open(texto, '', {
            duration: 10000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: ['custom-snackbar']
        });
    }

    protected irDetalhesHistorico(historico: number) {
        this.dialog.open(DiariaHistoricoDetalheComponent, {
            data: { 
                historicoId: historico,
            },
        });
    }

    decisaoMap: { [key: string]: string } = {
        'deferido': 'Deferido',
        'indeferido': 'Indeferido',
        'encaminhado': 'Encaminhado',
        'ciente': 'Ciente do cancelamento',
        'valor_alterado': 'Valor deferido alterado',
        'importacao': 'Importação',
        'recebido': 'Recebido',
        'liberado': 'Liberado',
    };
}