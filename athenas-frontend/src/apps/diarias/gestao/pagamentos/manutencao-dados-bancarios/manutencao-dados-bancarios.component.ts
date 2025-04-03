import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { apiRhDadosBancariosServidorContas } from 'api/rh/api-rh-dados-bancarios-servidor-contas.service';
import { NovaContaComponent } from 'apps/vdf/minhas-diarias/nova-conta/nova-conta.component';
import { apiRhSevidorService } from 'api/rh/api-rh-servidor.service';
import { apiDiariasBeneficiario } from 'api/diarias/api-diarias-beneficiario.service';
import { apiDiariasBeneficiarioEditar } from 'api/diarias/api-diarias-editar-beneficiario.service';

class ManutencaoDadosBancariosComponentData {
    servidor_id: number;
    beneficiario_id: number;
    onClose?: Function;
}

@Component({
    selector: 'manutencao-dados-bancarios',
    templateUrl: 'manutencao-dados-bancarios.component.html',
    standalone: false
})
export class ManutencaoDadosBancariosComponent extends MpmtFormularioComponent<ManutencaoDadosBancariosComponentData> {
    
    lista_contas: any[] =[];
    servidor: any = null;

    protected formulario = new FormGroup({
        conta: new FormControl<number[]>(null, [Validators.required]),
        
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: ManutencaoDadosBancariosComponentData,
        protected dialogRef: MatDialogRef<ManutencaoDadosBancariosComponentData>,
        protected snackBar: MatSnackBar,
        public dialog: MatDialog,

    ) {
        super(data, snackBar, dialogRef);
    }

    ngOnInit() {
        this.carregarDadosServidor();
        this.carregarContas();
        this.carregarDados();

    }

    async carregarDados() {
        if (this.data.beneficiario_id != null) {
            const results = await apiDiariasBeneficiario({
                id: this.data.beneficiario_id
            });
            this.formulario.get('conta')?.setValue([results.conta_bancaria_pgto]);
        }

    }



    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { conta } = this.formulario.value;

        if (this.data.beneficiario_id != null) {
            try {

                const { } = await apiDiariasBeneficiarioEditar
                    ({
                        id: this.data.beneficiario_id,
                        conta_bancaria_pgto: conta[0]
                    });

                this.exibirMensagem('', 'Beneficiário atualizado com sucesso.','sucess-snackbar')
                this.fecharFormulario();
                this.data?.onClose();
    
            } catch (e: any) {
                console.error(e)
                const detalheErro = e?.response?.data?.message || '';
                const texto = `Ocorreu um erro inesperado ao salvar rascunho. ${detalheErro}`;
                this.exibirMensagem('Aviso', texto);
            }
        }else{
        
            this.dialogRef.close({
                conta: conta[0]
                });
        }
    }
  
    public async carregarContas() {
        try {
            this.lista_contas = (await apiRhDadosBancariosServidorContas({servidor_id:this.data.servidor_id})).results;
        } catch (error) {
            console.error('Erro ao carregar as contas do servidor:', error);
        }
    }

    public async carregarDadosServidor() {
        try {
            this.servidor = (await apiRhSevidorService({id:this.data.servidor_id}));
        } catch (error) {
            console.error('Erro ao carregar dados do servidor:', error);
        }
    }

    protected irAdicionarNovaConta() {
        
        const d_conta =  this.dialog.open(NovaContaComponent, {
            data: { servidor_id: this.data.servidor_id },
        });


        d_conta.afterClosed().subscribe(result => {
            if (result) {    
                this.formulario.get('conta')?.setValue([result.conta]);
                this.carregarContas();
            }
        });
    }
}
