import { Component, Inject, ViewChild } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { printDate } from 'utils/print-date';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiDiariasDestinoCriar } from 'api/diarias/api-diarias-novo-destino.service';
import { apiRhStates } from 'api/rh/api-rh-estados.service';
import { apiRhLocations } from 'api/rh/api-rh-locations.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { MpmtSelecaoFormComponent, MpmtSelecaoFormComponentConfiguracao } from 'components/mpmt-selecao-form/mpmt-selecao-form.component';
import { apiDiariasDestino } from 'api/diarias/api-diarias-destino.service';
import { apiDiariasDestinoEditar } from 'api/diarias/api-diarias-editar-destino.service';
import { DiariaStepperService } from '../stepper/diaria-stepper.service';
import { apiDiariasViagem } from 'api/diarias/api-diarias-viagem.service';
import { apiDiariasEventos } from 'api/diarias/api-diarias-eventos.service';
import { DateAdapter } from '@angular/material/core';


class NovoDestinoComponentData {
    destino_id?: number;
    beneficiario_id: number;
    tipo_viagem?: string;
    onClose?: Function;
}

@Component({
    selector: 'novo-destino',
    templateUrl: './novo-destino.component.html',
    standalone: false
})
export class NovoDestinoComponent extends MpmtFormularioComponent<NovoDestinoComponentData> {
    printDate = printDate;

    servidor: any = null;
    viagem: any = null;
    dataInicio: any = null;
    dataFim: any = null;

    eventos: any[] = null;

    pais_origem_selecionado: number = 1;
    pais_destino_selecionado: number = 1;
    uf_origem_selecionado: number = this.data.tipo_viagem == "ESTADUAL" ? 79 : null;
    uf_destino_selecionado: number = this.data.tipo_viagem == "ESTADUAL" ? 79 : null;

    lista_uf_origem: any[] = [];
    uf_origem_busca: string = '';

    carregandoMunicipioOrigem: boolean = false;
    carregandoMunicipioDestino: boolean = false;

    municipioOrigemDisabled: boolean = true;
    municipioDestinoDisabled: boolean = true;

    @ViewChild('selecaoMunicipioOrigemComponent') selecaoMunicipioOrigemComponent: MpmtSelecaoFormComponent;
    @ViewChild('selecaoUfOrigemComponent') selecaoUfOrigemComponent: MpmtSelecaoFormComponent;

    @ViewChild('selecaoMunicipioDestinoComponent') selecaoMunicipioDestinoComponent: MpmtSelecaoFormComponent;
    @ViewChild('selecaoUfDestinoComponent') selecaoUfDestinoComponent: MpmtSelecaoFormComponent;

    protected formulario = new FormGroup({
        evento: new FormControl<number>(null, [Validators.required]),
        uf_origem: new FormControl<number>(null, [Validators.required]),
        municipio_origem: new FormControl<number>(null, [Validators.required]),
        uf_destino: new FormControl<number>(null, [Validators.required]),
        municipio_destino: new FormControl<number>(null, [Validators.required]),
        forma_deslocamento: new FormControl<string>(null, [Validators.required]),
        pref_turno_ida: new FormControl<string>(null, [Validators.required]),
        data: new FormControl<Date>(null, [Validators.required]),
        hora: new FormControl<string>(null, [Validators.required]),
        com_motorista: new FormControl<boolean>(false, []),
        veiculo_daa: new FormControl<boolean>(false, []),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: NovoDestinoComponentData,
        protected dialogRef: MatDialogRef<NovoDestinoComponentData>,
        protected snackBar: MatSnackBar,
        private stepperService: DiariaStepperService,
        protected dateAdapter: DateAdapter<Date>,
    ) {
        super(data, snackBar, dialogRef);
        this.dateAdapter.setLocale('pt-BR');
    }

    ngAfterViewInit() {
        this.formulario.get('uf_origem').valueChanges.subscribe(value => {
            this.uf_origem_selecionado = value;
            this.selecaoMunicipioOrigemComponent.limparSelecao();
            this.municipioOrigemDisabled = !value;
        });

        this.formulario.get('uf_destino').valueChanges.subscribe(value => {
            this.uf_destino_selecionado = value;
            this.selecaoMunicipioDestinoComponent.limparSelecao();
            this.municipioDestinoDisabled = !value;
        });

        if(this.data.tipo_viagem == "ESTADUAL"){
            this.formulario.get('uf_origem').setValue(79);
            this.formulario.get('uf_destino').setValue(79);
        }

        this.formulario.get('forma_deslocamento').valueChanges.subscribe(value => {
            const mostrarCheckboxes = value === '2'; // '2' é o id de Veículo institucional
            if (!mostrarCheckboxes) {
                this.formulario.get('com_motorista').setValue(false);
                this.formulario.get('veiculo_daa').setValue(false);
            }
        });


        this.carregarDados();
        this.carregarDadosViagem();
    }

    ngOnInit() {
        this.loadEventos()
    }

    async carregarDados() {
        if (this.data.destino_id != null) {
            const results = await apiDiariasDestino({
                id: this.data.destino_id
            });

            this.formulario.get('evento')?.setValue(results.evento);

            this.formulario.get('uf_origem')?.setValue(results.uf_origem);
            this.formulario.get('uf_destino')?.setValue(results.uf_destino);
            this.selecaoMunicipioOrigemComponent.limparSelecao();
            this.selecaoMunicipioDestinoComponent.limparSelecao();

            this.formulario.get('municipio_origem')?.setValue(results.municipio_origem);
            this.formulario.get('municipio_destino')?.setValue(results.municipio_destino);
            this.formulario.get('forma_deslocamento')?.setValue(results.forma_deslocamento);
            this.formulario.get('pref_turno_ida')?.setValue(results.pref_turno_ida);
            this.formulario.get('com_motorista')?.setValue(results.com_motorista);
            this.formulario.get('veiculo_daa')?.setValue(results.veiculo_daa);
            
            const datetime = new Date(results.data);
            const date = this.dateAdapter.parse(results.data, 'yyyy-MM-dd');
            const time = datetime.toTimeString().split(' ')[0].slice(0, 5);

            this.formulario.get('data')?.setValue(date);
            this.formulario.get('hora')?.setValue(time);
        }
    }

    async carregarDadosViagem() {
        if (this.stepperService.id_viagem != null) {
            const results = await apiDiariasViagem({
                id: this.stepperService.id_viagem
            });

            if (results) {
                this.dataInicio = results.data_inicio_viagem;
                this.dataFim = results.data_fim_viagem;
            }
        }
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const municipio_origem = this.selecaoMunicipioOrigemComponent.form_control.value;
        const municipio_destino = this.selecaoMunicipioDestinoComponent.form_control.value;

        const { uf_origem, uf_destino, forma_deslocamento, pref_turno_ida, data, hora , evento, com_motorista, veiculo_daa} = this.formulario.value;
        const formattedDate = new Date(data);
        const formattedTime = hora.split(':');

        formattedDate.setHours(parseInt(formattedTime[0]), parseInt(formattedTime[1]));
    
        const utcDatetime = new Date(formattedDate.getTime() - formattedDate.getTimezoneOffset() * 60000);

        try {
            if (this.data.destino_id == null) {
                const result = await apiDiariasDestinoCriar({
                    beneficiario: this.data.beneficiario_id,
                    evento: evento,
                    forma_deslocamento: forma_deslocamento,
                    pref_turno_ida: pref_turno_ida,
                    data: utcDatetime,
                    uf_origem: uf_origem,
                    municipio_origem: municipio_origem,
                    uf_destino: uf_destino,
                    municipio_destino: municipio_destino,
                    com_motorista: com_motorista,
                    veiculo_daa: veiculo_daa,
                });
            } else {
                const result = await apiDiariasDestinoEditar({
                    id: this.data.destino_id,
                    beneficiario: this.data.beneficiario_id,
                    evento: evento,
                    forma_deslocamento: forma_deslocamento,
                    pref_turno_ida: pref_turno_ida,
                    data: utcDatetime,
                    uf_origem: uf_origem,
                    municipio_origem: municipio_origem,
                    uf_destino: uf_destino,
                    municipio_destino: municipio_destino,
                    com_motorista: com_motorista,
                    veiculo_daa: veiculo_daa,
                });
            }

            this.fecharFormulario();
            this.data?.onClose();

        } catch (e: any) {
            console.log(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = detalheErro == '' ?  `Ocorreu um erro inesperado ao criar Destino.` : detalheErro;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }
    }

    selecaoUfOrigem: MpmtSelecaoFormComponentConfiguracao = {
        obterFiltros: payload => {
            return { palavra_chave: payload.palavra_chave, pais: this.pais_origem_selecionado, order_by: 'nome' };
        },
        obterOpcoes: apiRhStates,
        obterTitulo: 'name',
    };

    selecaoMunicipioOrigem: MpmtSelecaoFormComponentConfiguracao = {
        obterFiltros: payload => {
            return { palavra_chave: payload.palavra_chave, estado: this.uf_origem_selecionado, order_by: 'nome' };
        },
        obterOpcoes: async (payload) => {
            if (!payload.palavra_chave) {
                this.carregandoMunicipioOrigem = true;
            }
            const response = await apiRhLocations(payload);
            if (!payload.palavra_chave) {
                this.carregandoMunicipioOrigem = false;
            }
            return response;
        },
        obterTitulo: 'name',
    };

    selecaoUfDestino: MpmtSelecaoFormComponentConfiguracao = {
        obterFiltros: payload => {
            return { palavra_chave: payload.palavra_chave, pais: this.pais_destino_selecionado, order_by: 'nome' };
        },
        obterOpcoes: apiRhStates,
    };

    selecaoMunicipioDestino: MpmtSelecaoFormComponentConfiguracao = {
        obterFiltros: payload => {
            return { palavra_chave: payload.palavra_chave, estado: this.uf_destino_selecionado, order_by: 'nome' };
        },
        obterOpcoes: async (payload) => {
            if (!payload.palavra_chave) {
                this.carregandoMunicipioDestino = true;
            }
            const response = await apiRhLocations(payload);
            if (!payload.palavra_chave) {
                this.carregandoMunicipioDestino = false;
            }
            return response;
        },
        obterTitulo: 'name',
    };

    formas_deslocamento = [
        { id: '0', descricao: 'Veículo próprio' },
        { id: '1', descricao: 'Avião' },
        { id: '2', descricao: 'Veículo institucional' },
    ];

    turnos = [
        { id: 'MANHA', descricao: 'Manhã' },
        { id: 'TARDE', descricao: 'Tarde' },
        { id: 'NOITE', descricao: 'Noite' },
    ];

    protected get viagemEstadual(){
        return this.data.tipo_viagem == "ESTADUAL" ? true : false;
    }

    async loadEventos() {
        const { results } = await apiDiariasEventos({
            beneficiario: this.data.beneficiario_id
        });
        this.eventos = results;
    }
}
