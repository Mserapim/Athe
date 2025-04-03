import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { apiDiariasBeneficiarios } from 'api/diarias/api-diaria-beneficiarios.service';
import { DiariaStepperService } from '../stepper/diaria-stepper.service';
import { apiDiariasClonarDestino } from 'api/diarias/api-diarias-clonar-destino.service';
import { apiDiariasClonarLoteDestino } from 'api/diarias/api-diarias-clonar-lote-destinos.service';

class ClonarDestinosComponentData {
    beneficiario_base: number;
    destino?: number;
    destinos?: any[];
    onClose?: Function;
}

@Component({
    selector: 'clonar-destinos',
    templateUrl: 'clonar-destinos.component.html',
    standalone: false
})
export class ClonarDestinosComponent extends MpmtFormularioComponent<ClonarDestinosComponentData> {
    
    lista_beneficiarios: any[] =[];
    destinos: any[] = [];

    protected formulario = new FormGroup({
        beneficiarios: new FormControl<number[]>(null, [Validators.required]),        
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: ClonarDestinosComponentData,
        protected dialogRef: MatDialogRef<ClonarDestinosComponentData>,
        protected snackBar: MatSnackBar,
        public dialog: MatDialog,
        private stepperService: DiariaStepperService,

    ) {
        super(data, snackBar, dialogRef);
    }

    ngOnInit() {
        this.carregarBeneficiarios();
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { beneficiarios } = this.formulario.value;

        let result = null

        try {
            if(this.data.destino != null){
                result = await apiDiariasClonarDestino({
                    id: this.data.destino,
                    beneficiarios: beneficiarios
                });
            }else{
                result = await apiDiariasClonarLoteDestino({
                    beneficiario_base: beneficiarios[0],
                    beneficiarios: [this.data.beneficiario_base]
                });
            }
            this.exibirMensagem('', "Destinos clonados com sucesso.",'sucess-snackbar')

            this.fecharFormulario();
            this.data?.onClose();

        } catch (e: any) {
            const detalheErro = e?.response?.data?.error || '' ||  e?.response?.data?.datail;
            const texto = ` ${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }
    }
  
    public async carregarBeneficiarios() {
        try {
            this.lista_beneficiarios = (await apiDiariasBeneficiarios(
                {
                    viagem_id:this.stepperService.id_viagem,
                    exclude: [this.data.beneficiario_base]
                }
            )).results;
        } catch (error) {
            console.error('Erro ao carregar os beneficiários:', error);
        }
    }


}
