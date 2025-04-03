import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { NovaDiariaStep3Service } from './destinos-step3.service';
import { DiariaStepperService } from '../../stepper/diaria-stepper.service';
import { NovoDestinoComponent } from '../../novo-destino/novo-destino.component';
import { ClonarDestinosComponent } from '../../clonar-destinos/clonar-destinos.component';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiDiariasBeneficiario } from 'api/diarias/api-diarias-beneficiario.service';
import { FuseConfirmationService } from '@fuse/services/confirmation';
import { apiDiariasDestinoApagar } from 'api/diarias/api-diarias-apagar-destino.service';
import moment from 'moment';
import { apiDiariasViagem } from 'api/diarias/api-diarias-viagem.service';
import { apiDiariasViagemFinalizar } from 'api/diarias/api-diarias-nova-viagem-finalizar.service';


@Component({
    selector: 'destinos-step3',
    templateUrl: './destinos-step3.component.html',
    styleUrls: ['./destinos-step3.component.scss'],
    standalone: false
})
export class NovaDiariaStep3Component {
    titulo = 'Destinos';

    viagem: any = null;

    constructor(
        private stepperService: DiariaStepperService,
        public service: NovaDiariaStep3Service,
        public currentUserService: CurrentUserService,
        private router: Router,
        public dialog: MatDialog,
        protected snackBar: MatSnackBar,
        private _fuseConfirmationService: FuseConfirmationService


    ) {
        this.stepperService.currentStep = 2;
    }


    ngOnInit() {
        this.carregarViagem()
        this.configurarColunasItem();
        this.configurarColunasSubItem();
        this.service.recarregarListagem();
        this.validarStep();
    }

    private configurarColunasItem() {
        this.service.configurarColunasItem([
            {
                codigo: 'id',
                titulo: 'id',
                visivel: false,
            },
            {
                codigo: 'servidor_unicode',
                titulo: 'servidor_unicode',
                visivel: true,
            },
            {
                codigo: 'cargo',
                titulo: 'cargo',
                visivel: true,
            },
            {
                codigo: 'qtd_destinos',
                titulo: 'Quantidade de destinos:',
                visivel: true,
                transformarValor:  (linha: any) => {
                    return 'Quantidade de destinos: ' + linha;
                }
            },

            {
                codigo: 'total_distancia_destinos',
                titulo: 'Distância em km:',
                visivel: true,
                transformarValor:  (linha: any) => {
                    return linha ?'Distância em km: ' + linha : 'Distância em km: - ';
                }
            },
        ]);
    }

    private configurarColunasSubItem() {
        this.service.configurarColunasSubItem([
            {
                codigo: 'id',
                titulo: 'id',
                visivel: false,
                ordenavel: false,
            },
            {
                codigo: 'uf_origem_display',
                titulo: 'Origem',
                visivel: true,
                ordenavel: false,
                transformarValor:  (linha: any) => {
                    return linha.uf_origem_sigla + "/" + linha.municipio_origem_display;
                }
            },
            {
                codigo: 'uf_destino_display',
                titulo: 'Destino',
                visivel: true,
                ordenavel: false,
                transformarValor:  (linha: any) => {
                    return linha.uf_destino_sigla + "/" + linha.municipio_destino_display;
                }
            },
            {
                codigo: 'forma_deslocamento_display',
                titulo: 'Forma de deslocamento',
                visivel: true,
                ordenavel: false,
            },
            {
                codigo: 'pref_turno_ida_display',
                titulo: 'Preferência de turno',
                visivel: true,
                ordenavel: false,
            },
            {
                codigo: 'data',
                titulo: 'Data',
                tipo:'DATA',
                visivel: true,
                ordenavel: false,
            },
            {
                codigo: 'hora',
                titulo: 'Horário',
                visivel: true,
                ordenavel: false,
                transformarValor:  (linha: any) => {
                    return linha.data ? moment(linha.data).format('HH:mm') : '';
                }
            },
            {
                codigo: 'distancia_km',
                titulo: 'Distância em km',
                visivel: true,
                ordenavel: false,
                transformarValor:  (linha: any) => {
                    return linha.distancia_km ? linha.distancia_km + " km" : ' - ';
                }
            },
            {
                codigo: 'evento_display',
                titulo: 'Evento',
                visivel: false,
                ordenavel: false,
            },
            {
                codigo: 'com_motorista',
                titulo: 'Com motorista',
                tipo:'BOLEANO_ICONE',
                visivel: true,
                ordenavel: false,
            },
            {
                codigo: 'veiculo_daa',
                titulo: 'Veículo do DAA',
                tipo:'BOLEANO_ICONE',
                visivel: true,
                ordenavel: false,
            },
            {
                codigo: 'acoes',
                tipo: 'ACOES',
                ordenavel: false,
                visivel: true,
                acoes: [
                    {
                        icone: 'edit',
                        titulo: 'Editar',
                        aoClicar: (linha: any) => this.irEditarDestino(linha),
                    },
                    {
                        icone: 'cancel',
                        titulo: 'Apagar',
                        aoClicar: (linha: any) => this.irApagarDestino(linha),
                    },
                    {
                        icone: 'content_copy',
                        titulo: 'Clonar',
                        aoClicar: (linha: any) =>{
                            this.dialog.open(ClonarDestinosComponent, {
                                data: { 
                                    beneficiario_base: linha.beneficiario,
                                    destino: linha.id,
                                    destinos: [linha],
                                    onClose: () => this.service.recarregarListagem(),
                                },
                                panelClass: 'dialog-panel-gray-100',
                            });
                        } ,
                    },
                ],
            },
        ]);
    }

    irAnterior() {
        this.router.navigate([
            'vdf/minhas-diarias/nova/diaria',
            'step2',
        ]);
    }

    protected async irFinalizar() {

        try {
                        
            const result = await apiDiariasViagemFinalizar({
                id: this.viagem.id
            });
            const resultado = result.data?.datail || "Solicitação Concluida"

            this.exibirMensagem('', resultado, 'sucess-snackbar')

            this.router.navigate([
                'vdf/minhas-diarias'
            ]);

        } catch (e: any) {
            const detalheErro = e?.response?.data?.error || '' ||  e?.response?.data?.datail;
            const texto = ` ${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }



    }


    protected irAdicionarDestino( id:number ) {
        this.dialog.open(NovoDestinoComponent, {
            data: {
                beneficiario_id: id,
                tipo_viagem: this.viagem.tipo_viagem,
                onClose: () => this.service.recarregarListagem(),
            },
        });
    }

    private validarStep(){
        if (this.stepperService.id_viagem == null && this.stepperService.currentStep != 0){
            this.router.navigate(['vdf/minhas-diarias']);
        }
    }

    protected async irClonarLoteDestino( beneficiario_id:number) {
        this.dialog.open(ClonarDestinosComponent, {
            data: { 
                beneficiario_base: beneficiario_id,
                destinos: (await this.service.obterDadosSubItem(beneficiario_id)).results,
                onClose: () => this.service.recarregarListagem(),
            },
        });
    }

    protected async irEditarDestino(linha: any) {
        const results = await apiDiariasBeneficiario({
            id: linha.beneficiario
        });

        if (results.fluxo == 2){
            this.dialog.open(NovoDestinoComponent, {
                data: {
                    destino_id: linha.id,
                    beneficiario_id: linha.beneficiario,
                    tipo_viagem: this.viagem.tipo_viagem,
                    onClose: () => this.service.recarregarListagem() 
                },
            });
        }else{
            this.exibirMensagem(
                'Atenção',
                'Não é possível editar o destino após o envio da solicitação.'
            );
        }

    }
    protected async irApagarDestino(linha: any) {
        const results = await apiDiariasBeneficiario({
            id: linha.beneficiario
        });

        if (results.fluxo == 2){
        
            const dialogRef = this._fuseConfirmationService.open({
                title: 'Confirmação',
                message: 'Você tem certeza que deseja apagar o destino: </br>'+ 
                linha.uf_origem_sigla + '/' + linha.municipio_origem_display + ' para ' +
                linha.uf_destino_sigla + '/' + linha.municipio_destino_display + '</br>' +
                'Data: ' + moment(linha.data).format('DD/MM/YYYY') + ' ?',
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
                        
                        result = await apiDiariasDestinoApagar({
                            id: linha.id
                        });
                        
                        this.exibirMensagem('', "Destino excluído com sucesso.")

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
        }else{
            this.exibirMensagem(
                'Atenção',
                'Não é possível apagar o destino após o envio da solicitação.'
            );
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

    public async carregarViagem() {
        const result = apiDiariasViagem({id:this.stepperService.id_viagem});
         this.viagem = (await result)
    }
}
