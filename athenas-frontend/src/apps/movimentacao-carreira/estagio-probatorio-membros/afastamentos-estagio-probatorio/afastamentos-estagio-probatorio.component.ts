import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { AfastamentoService } from './afastamentos-estagio-probatorio.service';

class AfastamentosEstagioProbatorioData {
    membroId: number;
    onClose?: Function;
}

@Component({
    selector: 'afastamentos-estagio-probatorio',
    templateUrl: 'afastamentos-estagio-probatorio.component.html',
    standalone: false
})
export class AfastamentosComponent extends MpmtFormularioComponent<AfastamentosEstagioProbatorioData> implements OnInit {
    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: AfastamentosEstagioProbatorioData,
        protected dialogRef: MatDialogRef<AfastamentosEstagioProbatorioData>,
        protected snackBar: MatSnackBar,
        protected service: AfastamentoService,
    ) {
        super(data, snackBar, dialogRef);
    }

    async ngOnInit() {        
        this.service.membroId = this.data?.membroId;
        await this.service.recarregarListagem();
        this.configurarColunas();
    }
    

    private configurarColunas() {
        this.service.configurarColunas([
            {
                codigo: 'id',
                titulo: 'Id',
                visivel: false,
            },
            {
                codigo: 'afastamento_unicode',
                titulo: 'Descrição',
                visivel: false,
            },
            {
                codigo: 'servidor_unicode',
                titulo: 'Membro',
                visivel: true,
            },
            {
                codigo: 'situation_unicode',
                titulo: 'Afastamento',
                visivel: true,
            },
            {
                codigo: 'tipo',
                titulo: 'Tipo',
                visivel: true,
            },
            {
                codigo: 'data_inicio',
                titulo: 'Data início',
                tipo:'DATA',
                visivel: true,
                ordenavel: false,
            },
            {
                codigo: 'data_fim',
                titulo: 'Data fim',
                tipo:'DATA',
                visivel: true,
                ordenavel: false,
            },
            {
                codigo: 'qtd_dias',
                titulo: 'Qtd. dias',
                visivel: true,
                ordenavel: false,
            },
        ]);
    }

}
