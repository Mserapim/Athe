import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { apiDiariasBeneficiarios } from 'api/diarias/api-diaria-beneficiarios.service';
import { apiDiariasViagemCancelar } from 'api/diarias/api-diarias-nova-viagem-cancelar.service';

class CancelarDiariaComponentData {
    viagem_id: number;
    solicitante: boolean;
    currentUser: any;
    onClose?: Function;
}

@Component({
    selector: 'cancelar-diaria',
    templateUrl: 'cancelar-diaria.component.html',
    standalone: false
})
export class CancelarDiariaComponent extends MpmtFormularioComponent<CancelarDiariaComponentData> {
    
    lista_beneficiarios: any[] =[];

    protected formulario = new FormGroup({
        beneficiarios: new FormControl<number[]>(null, [Validators.required]),        
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: CancelarDiariaComponentData,
        protected dialogRef: MatDialogRef<CancelarDiariaComponentData>,
        protected snackBar: MatSnackBar,
        public dialog: MatDialog,
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

            result = await apiDiariasViagemCancelar({
                id: this.data.viagem_id,
                beneficiarios_ids: beneficiarios
            });
            
            const resultado = result.data?.datail || "Solicitação Cancelada"

            this.exibirMensagem('', resultado, 'sucess-snackbar')

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
                    viagem_id:this.data.viagem_id
                }
            )).results;
        } catch (error) {
            console.error('Erro ao carregar os beneficiários:', error);
        }
    }

    protected opcao_ativa(beneficiario): boolean{
        if(beneficiario.fluxo_unicode.toUpperCase().includes("CANCELADO")){
            return true
        }

        if(this.data.solicitante){
            return false
        }
        if(beneficiario.servidor == this.data.currentUser.id){
            return false
        }

        return true
    }


}
