import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { MpmtVerMaisComponent } from 'components/mpmt-ver-mais/mpmt-ver-mais.component';

class AuditoriaLogsData {
    linha: any = {};
}

@Component({
    selector: 'modal-auditoria-logs',
    templateUrl: 'modal-auditoria-logs.component.html',
    standalone: false
})
export class AuditoriaLogsModalComponent extends MpmtFormularioComponent<AuditoriaLogsData> implements OnInit {
    displayedColumns: string[] = ['campo', 'anterior', 'novo'];

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: AuditoriaLogsData,
        protected dialogRef: MatDialogRef<AuditoriaLogsData>,
        protected snackBar: MatSnackBar,
        public dialog: MatDialog,
    ) {
        super(data, snackBar, dialogRef);
    }

    async ngOnInit() {        
    }

    getNomeCampo(alteracao: any): string {
        return Object.keys(alteracao)[0];
    }
    
    getValorAnterior(alteracao: any): any {
        const campo = Object.keys(alteracao)[0];
        return alteracao[campo]?.anterior ?? '-';
    }
    
    getValorNovo(alteracao: any): any {
        const campo = Object.keys(alteracao)[0];
        return alteracao[campo]?.novo ?? '-';
    }

    abrirDetalhes(alteracao: any, tipo: 'anterior' | 'novo') {
        this.dialog.open(MpmtVerMaisComponent, {
          width: '500px',
          data: { 
            titulo: tipo === 'anterior' ? 'Valor anterior' : 'Valor novo', 
            conteudo: tipo === 'anterior' ? this.getValorAnterior(alteracao) : this.getValorNovo(alteracao)
          }
        });
    }

}
