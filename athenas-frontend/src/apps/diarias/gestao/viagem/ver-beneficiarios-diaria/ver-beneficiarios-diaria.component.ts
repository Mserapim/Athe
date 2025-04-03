import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiDiariasBeneficiarios } from 'api/diarias/api-diaria-beneficiarios.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';


class ListaBeneficiariosDiariasComponentData {
    id: number;
}

@Component({
    selector: 'ver-beneficiarios-diaria',
    templateUrl: './ver-beneficiarios-diaria.component.html',
    standalone: false
})
export class ListaBeneficiariosDiariasComponent extends MpmtFormularioComponent<ListaBeneficiariosDiariasComponentData> {
    beneficiarios: any = [];
    
    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: ListaBeneficiariosDiariasComponentData,
        protected dialogRef: MatDialogRef<ListaBeneficiariosDiariasComponentData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }
    
    ngOnInit() {
        this.carregarDados();
    }

    async carregarDados() {
        await this.carregarBeneficiarios();
    }
    
    async carregarBeneficiarios() {
        const viagem_id = this.data.id;
        try {
            const beneficiarios = await apiDiariasBeneficiarios({ 
                viagem_id: viagem_id,
             });
            this.beneficiarios = beneficiarios.results
        } catch (e: any) {
        console.error('Erro ao buscar dados', e);
        }
    }
}