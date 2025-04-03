import { Component, Inject, ViewChild } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiRhSevidoresService } from 'api/rh/api-rh-servidores.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { MpmtSelecaoComponent, MpmtSelecaoComponentConfiguracao } from 'components/mpmt-selecao/mpmt-selecao.component';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { apiDiariasBeneficiarioCriar } from 'api/diarias/api-diarias-novo-beneficiario.service';
import { DiariaStepperService } from '../stepper/diaria-stepper.service';
import { NovoDadosBancariosComponent } from '../novo-dados-bancarios/novo-dados-bancarios.component';
import { NovoColaboradorEventualComponent } from '../novo-colaborador-eventual/novo-colaborador-eventual.component';
import { FormularioBeneficiarioComponent } from '../formulario-beneficiario/formulario-beneficiario.component';


class NovoBeneficiarioComponentData {
    onClose?: Function;
}

@Component({
    selector: 'novo-beneficiario',
    templateUrl: './novo-beneficiario.component.html',
    styleUrls: ['./novo-beneficiario.component.scss'],
    standalone: false
})
export class NovoBeneficiarioComponent extends MpmtFormularioComponent<NovoBeneficiarioComponentData> {

    @ViewChild('selecaoServidorComponent') selecaoServidorComponent: MpmtSelecaoComponent;

    tipo_posse = null;
    tipo_posse_exclude = null;
    origem_servidor = true;

    loading = false; // Variável de controle para o estado de carregamento

    protected formulario = new FormGroup({
        servidor_mpmt: new FormControl<boolean>(true, [Validators.required]),
        servidor: new FormControl<number>(null, [Validators.required]),
       
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: NovoBeneficiarioComponentData,
        protected dialogRef: MatDialogRef<NovoBeneficiarioComponentData>,
        protected snackBar: MatSnackBar,
        private stepperService: DiariaStepperService,
        public dialog: MatDialog,
        public currentUserService: CurrentUserService,

    ) {
        super(data, snackBar, dialogRef);
    }

    protected alterar_tipo_beneficiario(){
        const { servidor_mpmt  } = this.formulario.value;
        
        if(servidor_mpmt){
            this.tipo_posse = null;
            this.tipo_posse_exclude = ['COE', 'TCR'];
            this.origem_servidor = true;
        }else{
            this.tipo_posse = ['COE', 'TCR'];
            this.tipo_posse_exclude = null ;
            this.origem_servidor = false;

        }
        this.selecaoServidorComponent.resetarSelecao();

        this.formulario.get('servidor')?.setValue(null);
    }

    selecaoServidor: MpmtSelecaoComponentConfiguracao = {
        obterOpcoes: apiRhSevidoresService,
        obterTitulo: 'nome',
        obterFiltros: payload => {
            return { 
                per_page: 15,
                page:1,
                palavra_chave: payload.palavra_chave,
                situacao: true,
                tipo_posse: this.tipo_posse,
                tipo_posse_exclude: this.tipo_posse_exclude,
            }; 
        },
    };

    protected servidorSelecionado(){
        const { servidor  } = this.formulario.value;
        
        if (servidor != null) {
            return false
        }else{
            return true
        }
    }

    protected irDadosBancariosSolicitante() {
      
        this.formulario.get('servidor')?.setValue(this.currentUserService.currentUser.id);
        const d_conta =  this.dialog.open(NovoDadosBancariosComponent, {
            data: { servidor_id: this.currentUserService.currentUser.id },
            
        });


        d_conta.afterClosed().subscribe(result => {
            if (result) {
                this.salvarBeneficiario(result.conta);
            }
        });

    }

    protected irDadosBancariosServidor() {
        const { servidor  } = this.formulario.value;
      
        const d_conta =  this.dialog.open(NovoDadosBancariosComponent, {
            data: { servidor_id: servidor },
        });


        d_conta.afterClosed().subscribe(result => {
            if (result) {
                this.salvarBeneficiario(result.conta);
            }
        });
    }

    protected irCriarColaboradorEventual() {
             
        this.dialog.open(NovoColaboradorEventualComponent, {
            data: {
                onClose: () => {
                    this.fecharFormulario();
                    this.data?.onClose();
                },
            },
        });

    }

    
    protected async salvarBeneficiario(conta) {
    
        const { servidor  } = this.formulario.value;

        try {
            this.loading = true;
            const {id} = await apiDiariasBeneficiarioCriar({
                servidor: servidor,
                viagem: this.stepperService.id_viagem,
                conta_bancaria_pgto: conta

            });
            this.loading = false;

            this.resetarFormulario();
            this.fecharFormulario();

            this.dialog.open(FormularioBeneficiarioComponent, {
                data: {
                    servidor: servidor,
                    beneficiario: id,
                    onClose: () => {
                        
                        this.data?.onClose();
                    }
                },
            });




        } catch (e: any) {
            this.loading = false;
            console.error(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao salvar o módulo. ${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }
    }
    
}
