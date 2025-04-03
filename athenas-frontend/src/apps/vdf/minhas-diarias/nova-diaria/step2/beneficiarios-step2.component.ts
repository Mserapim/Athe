import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { NovaDiariaStep2Service } from './beneficiarios-step2.service';
import { DiariaStepperService } from '../../stepper/diaria-stepper.service';
import { NovoBeneficiarioComponent } from '../../novo-beneficiario/novo-beneficiario.component';
import { NovoDadosBancariosComponent } from '../../novo-dados-bancarios/novo-dados-bancarios.component';
import { MatSnackBar } from '@angular/material/snack-bar';
import { FuseConfirmationService } from '@fuse/services/confirmation';
import { apiDiariasBeneficiarioApagar } from 'api/diarias/api-diarias-apagar-beneficiario.service';
import { FormularioBeneficiarioComponent } from '../../formulario-beneficiario/formulario-beneficiario.component';


@Component({
    selector: 'beneficiarios-step2',
    templateUrl: './beneficiarios-step2.component.html',
    styleUrls: ['./beneficiarios-step2.component.scss'],
    standalone: false
})
export class NovaDiariaStep2Component {
    titulo = 'Beneficiarios';

    constructor(
        private stepperService: DiariaStepperService,
        public service: NovaDiariaStep2Service,
        public currentUserService: CurrentUserService,
        private router: Router,
        public dialog: MatDialog,
        protected snackBar: MatSnackBar,
        private _fuseConfirmationService: FuseConfirmationService

    ) {
        this.stepperService.currentStep = 1;
    }


    ngOnInit() {
        this.configurarColunas();
        this.service.recarregarListagem();
        this.validarStep();

    }

    private validarStep(){
        if (this.stepperService.id_viagem == null && this.stepperService.currentStep != 0){
            this.router.navigate(['vdf/minhas-diarias']);
        }
    }


    private configurarColunas() {
        this.service.configurarColunas([
            {
                codigo: 'id',
                titulo: 'Código',
                visivel: false,
            },
            {
                codigo: 'servidor_unicode',
                titulo: 'Matrícula - Nome',
                visivel: true,
            },
            {
                codigo: 'cargo',
                titulo: 'Cargo',
                visivel: true,
            },
            {
                codigo: 'conta_bancaria_unicode',
                titulo: 'Dados bancários',
                ordenavel: false,
                visivel: true,

            },
            {
                codigo: 'situacao_solicitacao_display',
                titulo: 'Situação da solicitação',
                ordenavel: false,
                visivel: false,

            },
            {
                codigo: 'etapa_solicitacao_display',
                titulo: 'Etapa da solicitação',
                ordenavel: false,
                visivel: false,

            },
            {
                codigo: 'acoes',
                tipo: 'ACOES',
                ordenavel: false,
                acoes: [
                    {
                        titulo: 'Editar',
                        icone: 'edit',
                        aoClicar: (linha: any) => this.irEditarBeneficiario(linha),
                    },
                    {
                        titulo: 'Apagar',
                        icone: 'cancel',
                        aoClicar: (linha: any) => this.irApagarBeneficiario(linha),
                    },
                ],
            },
        ]);
    }


    protected irNovoBeneficiario() {
        this.dialog.open(NovoBeneficiarioComponent, {
            height: '70%',
            data: { onClose: () => this.service.recarregarListagem() },
        });

    }

    protected irEditarBeneficiario(linha: any) {
        if (linha.fluxo == 2){
            this.dialog.open(FormularioBeneficiarioComponent, {
                data: {
                    servidor: linha.servidor,
                    beneficiario: linha.id,
                    onClose: () => this.service.recarregarListagem() 
                },
            });
        }else{
            this.snackBar.open('', 'Não é possível editar o beneficiário após o envio da solicitação.', {
                duration: 10000,
                horizontalPosition: 'center',
                verticalPosition: 'top',
                panelClass: ['custom-snackbar'],
            });
        }

    }

    protected irApagarBeneficiario(linha: any) {
        
        const dialogRef = this._fuseConfirmationService.open({
            title: 'Confirmação',
            message: 'Você tem certeza que deseja apagar o beneficiário '+ linha.servidor_unicode + ' ?',
            icon: {
              show: true,
              name: 'heroicons_outline:exclamation',
              color: 'warn'
            },
            actions: {
                confirm: {
                  show: true,
                  label: 'Apagar',
                  style: { 'background-color': '#dc2626' },                           
                },
                cancel: {
                  show: true,
                  label: 'Cancelar',
                  style: { 'background-color': '#cbd5e1' },
                }
              },
              dismissible: true
          });
      
          dialogRef.afterClosed().subscribe( async result => {
            if (result === 'confirmed') {
                try {
                    
                    result = await apiDiariasBeneficiarioApagar({
                        id: linha.id
                    });
                    
                    this.exibirMensagem('', result.datail)

                    this.service.recarregarListagem();
        
        
                } catch (e: any) {
                    const detalheErro = e?.response?.data?.error || '' ||  e?.response?.data?.datail;
                    const texto = ` ${detalheErro}`;
                    this.exibirMensagem(
                        'Atenção',
                        texto
                    );
                }
            }
          });

    }

    displayFn(row: any): string {
        if (row) return `${row?.nome}`;
        else return '';
    }

    irAnterior() {
        this.router.navigate([
            'vdf/minhas-diarias/nova/diaria',
            'step1',
        ]);
    }

    irProximo() {

        if (this.service.getTotalItems() > 0) {
            this.router.navigate([
                'vdf/minhas-diarias/nova/diaria',
                'step3',
            ]);
        } else {
            alert('Inclua pelo Menos um beneficiario para poder avançar');
        }
    }


    protected exibirMensagem(titulo: string, texto: string, classe: string = 'custom-snackbar') {
        this.snackBar.open(texto, '', {
            duration: 10000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: [classe],
        });
    }

    protected exibirErro(e: any) {
        const detalheErro = e?.response?.data?.message || '';
        const texto = `Ocorreu um erro inesperado ao salvar. ${detalheErro}`;
        this.snackBar.open(texto, '', {
            duration: 10000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: ['custom-snackbar'],
        });
    }


}
