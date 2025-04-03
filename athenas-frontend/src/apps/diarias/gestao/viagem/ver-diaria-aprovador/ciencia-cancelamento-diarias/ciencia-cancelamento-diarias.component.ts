import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiBeneficiariosPorFluxo } from 'api/diarias/api-diaria-beneficiarios-por-fluxo.service';
import { apiCienciaCancelamentoDiarias } from 'api/diarias/aprovacoes-beneficiario/api-ciencia-cancelamento.service';

export class CienciaCancelamentoComponentData {
    titulo: string;
    fluxoID: number;
    viagemID: number;
    onClose?: Function;
}

@Component({
    selector: 'ciencia-cancelamento-diarias',
    templateUrl: './ciencia-cancelamento-diarias.component.html',
    standalone: false
})
export class CienciaCancelamentoComponent implements OnInit{ 
    beneficiarios: any[] = [];
    constructor(
        @Inject(MAT_DIALOG_DATA) 
        protected data: CienciaCancelamentoComponentData,
        protected dialogRef: MatDialogRef<CienciaCancelamentoComponentData>,
        protected snackBar: MatSnackBar,
    ) {}

    async ngOnInit() {
        await this.carregarBeneficiarios();
    }

    protected async carregarBeneficiarios() {
        try {
            const payload = { fluxo_id: this.data.fluxoID, viagem_id: this.data.viagemID };
            const response = await apiBeneficiariosPorFluxo(payload);
            this.beneficiarios = response.results;
        } catch (error) {
            const detalheErro = error?.response?.data?.message || 'Erro ao carregar beneficiários.';
            this.exibirMensagem('Erro', detalheErro);
        }

    }

    protected async darCiencia() {
        try {
            const beneficiariosIds = this.beneficiarios.map((beneficiario) => beneficiario.id);

            const payload = {
                beneficiarios: beneficiariosIds,
            };
            await apiCienciaCancelamentoDiarias(payload);
            
            this.dialogRef.close(true);
        } catch (error) {
            const detalheErro = error?.response?.data?.message || 'Erro ao realizar ciência de cancelamento.';
            this.exibirMensagem('Erro', detalheErro);
        }
    }
    
    protected exibirMensagem(titulo: string, texto: string, classe: string = 'custom-snackbar') {
        this.snackBar.open(texto, '', {
            duration: 4000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: [classe],
        });
    }

    protected fecharFormulario() {
        this.dialogRef.close();
    }
}
