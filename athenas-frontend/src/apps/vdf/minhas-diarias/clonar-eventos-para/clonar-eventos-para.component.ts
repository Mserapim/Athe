import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { apiDiariasBeneficiarios } from 'api/diarias/api-diaria-beneficiarios.service';
import { DiariaStepperService } from '../stepper/diaria-stepper.service';
// import { apiDiariasClonarDestino } from 'api/diarias/api-diarias-clonar-destino.service';
import { apiDiariasClonarLoteEvento } from 'api/diarias/api-diarias-clonar-lote-eventos.service';
import { apiDiariasClonarEvento } from 'api/diarias/api-diarias-clonar-evento.service';

class ClonarEventosParaComponentData {
    beneficiario_base: number;
    evento?: number;
    eventos?: any[];
    onClose?: Function;
}

@Component({
    selector: 'clonar-eventos-para',
    templateUrl: 'clonar-eventos-para.component.html',
    standalone: false
})
export class ClonarEventosParaComponent extends MpmtFormularioComponent<ClonarEventosParaComponentData> {
    
    lista_beneficiarios: any[] =[];
    eventos: any[] = [];

    protected formulario = new FormGroup({
        beneficiarios: new FormControl<number[]>(null, [Validators.required]),        
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: ClonarEventosParaComponentData,
        protected dialogRef: MatDialogRef<ClonarEventosParaComponentData>,
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
            if(this.data.evento != null){
                result = await apiDiariasClonarEvento({
                    id: this.data.evento,
                    beneficiarios: beneficiarios
                });
            }else{
                result = await apiDiariasClonarLoteEvento({
                    beneficiario_base: this.data.beneficiario_base,
                    beneficiarios: beneficiarios
                });
            }
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
