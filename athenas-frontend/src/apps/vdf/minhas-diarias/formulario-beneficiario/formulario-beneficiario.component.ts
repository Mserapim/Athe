import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { DateAdapter } from '@angular/material/core';
import { DateRange } from '@angular/material/datepicker';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiDiariasEventoCriar } from 'api/diarias/api-diarias-evento-criar.service';
import { apiDiariasEventoEditar } from 'api/diarias/api-diarias-evento-editar.service';
import { apiDiariasEvento } from 'api/diarias/api-diarias-evento.service';
import { apiRhSevidorService } from 'api/rh/api-rh-servidor.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { formatDate } from 'utils/format-date';
import { FormularioEventoService } from './formulario-beneficiario-eventos.service';
import { FuseConfirmationService } from '@fuse/services/confirmation';
import { apiDiariasEventoApagar } from 'api/diarias/api-diarias-evento-apagar.service';
import { FormularioEventoComponent } from '../formulario-evento/formulario-evento.component';
import { NovaContaComponent } from '../nova-conta/nova-conta.component';
import { apiRhDadosBancariosServidorContas } from 'api/rh/api-rh-dados-bancarios-servidor-contas.service';
import { apiDiariasBeneficiario } from 'api/diarias/api-diarias-beneficiario.service';
import { ClonarEventosParaComponent } from '../clonar-eventos-para/clonar-eventos-para.component';
import { ClonarEventosDeComponent } from '../clonar-eventos-de/clonar-eventos-de.component';


class FormularioBeneficiarioComponentData {
    beneficiario?: number;
    servidor?: number;
    onClose?: Function;
}

@Component({
    selector: 'formulario-beneficiario',
    templateUrl: 'formulario-beneficiario.component.html',
    standalone: false
})
export class FormularioBeneficiarioComponent extends MpmtFormularioComponent<FormularioBeneficiarioComponentData> {

    servidor: any = null;
    lista_contas: any[] = [];
    eventos: any[] = [];

    protected formulario = new FormGroup({
        conta: new FormControl<number[]>(null, [Validators.required]),
       

    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: FormularioBeneficiarioComponentData,
        protected dialogRef: MatDialogRef<FormularioBeneficiarioComponentData>,
        protected snackBar: MatSnackBar,
        protected dateAdapter: DateAdapter<Date>,
        protected service_evento: FormularioEventoService,
        private _fuseConfirmationService: FuseConfirmationService,
        public dialog: MatDialog,


    ) {
        super(data, snackBar, dialogRef);
        this.dateAdapter.setLocale('pt-BR');
        this.service_evento.beneficiario_id = this.data.beneficiario;
        this.service_evento.recarregarListagem();

    }

    ngOnInit() {
        this.configurarColunas()
        this.carregarDados();
        this.carregarContas();
        this.service_evento.recarregarListagem();
        this.carregar_eventos()
    }
    
    async carregarDados() {
        try {
            this.servidor = (await apiRhSevidorService({id:this.data.servidor}));
        } catch (error) {
            console.error('Erro ao carregar dados do servidor:', error);
        }

        if (this.data.beneficiario != null) {
            const results = await apiDiariasBeneficiario({
                id: this.data.beneficiario
            });
            this.formulario.get('conta')?.setValue([results.conta_bancaria_pgto]);
        }
    }
    


    protected async confirmarFormulario() {
        if (!this.formularioValido) return;
    
        const {  } = this.formulario.value;


        try {

    
            this.fecharFormulario();
            this.data?.onClose();
        } catch (e: any) {
            console.error(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao processar o evento. ${detalheErro}`;
            this.exibirMensagem('Atenção', texto);
        }
    }
    
    
    private configurarColunas() {
        this.service_evento.configurarColunas([
            {
                codigo: 'id',
                titulo: 'Código',
                visivel: false,
            },
            {
                codigo: 'titulo',
                titulo: 'Título',
                visivel: true,
            },
            {
                codigo: 'data_inicio',
                titulo: 'Data início',
                tipo:'DATA',
                visivel: true,
            },
            {
                codigo: 'data_fim',
                titulo: 'Data fim',
                tipo:'DATA',
                visivel: true,
            },
            {
                codigo: 'acoes',
                tipo: 'ACOES',
                ordenavel: false,
                acoes: [
                    {
                        titulo: 'Editar',
                        icone: 'edit',
                        aoClicar: (linha: any) => this.irEditarEvento(linha),
                    },
                    {
                        titulo: 'Clonar',
                        icone: 'content_copy',
                        aoClicar: (linha: any) => {
                            this.dialog.open(ClonarEventosParaComponent, {
                                data: { 
                                    beneficiario_base: linha.beneficiario,
                                    evento: linha.id,
                                    eventos: [linha],
                                    onClose: () => this.service_evento.recarregarListagem(),
                                },
                                panelClass: 'dialog-panel-gray-100',
                            });
                        },
                    },
                    {
                        titulo: 'Apagar',
                        icone: 'cancel',
                        aoClicar: (linha: any) => this.irApagarEvento(linha),
                    },
                ],
            },
        ]);
    }



    protected irNovoEvento() {
        
        this.dialog.open(FormularioEventoComponent, {
            data: {
                beneficiario: this.data.beneficiario,
                onClose: () => this.service_evento.recarregarListagem() 
            },
        });
    }

    protected irEditarEvento(linha: any) {
        
        this.dialog.open(FormularioEventoComponent, {
            data: {
                evento: linha.id,
                beneficiario: this.data.beneficiario,
                onClose: () => this.service_evento.recarregarListagem() 
            },
        });
    }

    protected irApagarEvento(linha: any) {
        
        const dialogRef = this._fuseConfirmationService.open({
            title: 'Confirmação',
            message: 'Você tem certeza que deseja apagar o evento '+ linha.titulo + ' ?',
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
                    
                    result = await apiDiariasEventoApagar({
                        id: linha.id
                    });
                    
                    this.exibirMensagem('', result.datail)

                    this.service_evento.recarregarListagem();
        
        
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

    protected irAdicionarNovaConta() {
        
        const d_conta =  this.dialog.open(NovaContaComponent, {
            data: { servidor_id: this.data.servidor },
        });


        d_conta.afterClosed().subscribe(result => {
            if (result) {    
                this.formulario.get('conta')?.setValue([result.conta]);
                this.carregarContas();
            }
        });
    }
    
    public async carregarContas() {
        try {
            this.lista_contas = (await apiRhDadosBancariosServidorContas({servidor_id:this.data.servidor})).results;
        } catch (error) {
            console.error('Erro ao carregar as contas do servidor:', error);
        }
    }


    protected irClonarLoteParaEventos() {
        
        this.dialog.open(ClonarEventosParaComponent, {
            data: { 
                beneficiario_base: this.data.beneficiario,
                eventos: this.eventos,
                onClose: () => console.log(''),
            },
        });
    }


    protected irClonarLoteDeEventos() {
       
        this.dialog.open(ClonarEventosDeComponent, {
            data: { 
                beneficiario_base: this.data.beneficiario,
                eventos: this.eventos,
                onClose: () => this.service_evento.recarregarListagem(),
            },
        });
    }


    async carregar_eventos(){
        const filtros = { palavra_chave: "", beneficiario: this.data.beneficiario }
        this.eventos =  (await this.service_evento.obterDados(filtros)).results
    }


    protected get clonarValido() :boolean{
        return this.eventos?.length > 0
    }

    protected fecharFormulario() {
        this.data?.onClose();
        this.dialogRef.close();
    }
}
