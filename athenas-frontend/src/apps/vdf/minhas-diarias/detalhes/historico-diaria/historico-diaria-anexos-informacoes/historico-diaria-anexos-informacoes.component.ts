import { Component, Inject, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { useGedDownload } from 'api/@base/use-ged-download';
import { apiDiariasHistoricoAnexosInformacoes } from 'api/diarias/detalhe/api-historico-anexos-informacoes.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';

class DiariaHistoricoDetalheData {
    historicoId: number;
}

@Component({
    selector: 'historico-diaria-anexos-informacoes',
    templateUrl: 'historico-diaria-anexos-informacoes.component.html',
    standalone: false
})
export class DiariaHistoricoDetalheComponent extends MpmtFormularioComponent<DiariaHistoricoDetalheData> implements OnInit{
    historico: any = {};
    anexos: any = [];

    ngOnInit() {
        super.ngOnInit();
        this.carregarDadosHistorico();
    }

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: DiariaHistoricoDetalheData,
        protected dialogRef: MatDialogRef<DiariaHistoricoDetalheData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    async carregarDadosHistorico() {
        if(this.data.historicoId != null) {
            try {
                const historico = await apiDiariasHistoricoAnexosInformacoes({
                    historico_id: this.data.historicoId
                });

                this.historico = historico.results[0];
                this.anexos = this.historico.anexos;
            } catch (e: any) {
                const detalheErro = e?.response?.data?.message || 'Não foi possível carregar os dados.';
                this.exibirMensagem('Erro', detalheErro);
            }
        }
    }

    public async downloadAnexo(id) {
        useGedDownload(id);
    }
}
