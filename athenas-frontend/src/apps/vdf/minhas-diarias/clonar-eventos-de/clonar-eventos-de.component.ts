import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { apiDiariasBeneficiarios } from 'api/diarias/api-diaria-beneficiarios.service';
import { DiariaStepperService } from '../stepper/diaria-stepper.service';
// import { apiDiariasClonarDestino } from 'api/diarias/api-diarias-clonar-destino.service';
import { apiDiariasClonarLoteEvento } from 'api/diarias/api-diarias-clonar-lote-eventos.service';

class ClonarEventosDeComponentData {
    beneficiario_base: number;
    onClose?: Function;
}

@Component({
    selector: 'clonar-eventos-de',
    templateUrl: 'clonar-eventos-de.component.html',
    standalone: false
})
export class ClonarEventosDeComponent extends MpmtFormularioComponent<ClonarEventosDeComponentData> {
    
    lista_beneficiarios: any[] =[];

    protected formulario = new FormGroup({
        beneficiario: new FormControl<number[]>(null, [Validators.required]),        
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: ClonarEventosDeComponentData,
        protected dialogRef: MatDialogRef<ClonarEventosDeComponentData>,
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

        const { beneficiario } = this.formulario.value;

        let result = null

        try {
            
            result = await apiDiariasClonarLoteEvento({
                beneficiario_base: beneficiario[0],
                beneficiarios: [this.data.beneficiario_base]
            });
            
            this.exibirMensagem('', "eventos clonados com sucesso.",'sucess-snackbar')

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
