import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiBeneficiarioVeiculoMotorista } from 'api/diarias/detalhe/api-diarias-daa-veiculo-motorista.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';

class DaaMotoristaVeiculoData {
    destinoId: number;
    onClose?: Function;
}

@Component({
    selector: 'daa-motorista-veiculo',
    templateUrl: 'daa-motorista-veiculo.component.html',
    standalone: false
})
export class DaaMotoristaVeiculoComponent extends MpmtFormularioComponent<DaaMotoristaVeiculoData> implements OnInit {
    veiculoMotorista: any = [];

    ngOnInit() {
        super.ngOnInit();
        this.carregarDadosVeiculoMotorista();
    }

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: DaaMotoristaVeiculoData,
        protected dialogRef: MatDialogRef<DaaMotoristaVeiculoData>,
        protected snackBar: MatSnackBar,
    ) {
        super(data, snackBar, dialogRef);
    }

    async carregarDadosVeiculoMotorista() {
        if(this.data.destinoId != null) {
            try {
                const veiculoMotorista = await apiBeneficiarioVeiculoMotorista({
                    destinoId: this.data.destinoId
                });

                this.veiculoMotorista = veiculoMotorista.results[0];
                
            } catch (e: any) {
                const detalheErro = e?.response?.data?.message || 'Não foi possível carregar os dados.';
                this.exibirMensagem('Erro', detalheErro);
            }
        }
    }
}
