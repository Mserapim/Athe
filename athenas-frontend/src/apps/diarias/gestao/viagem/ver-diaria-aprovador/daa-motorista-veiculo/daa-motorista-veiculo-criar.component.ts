import { Component, Inject, OnInit } from '@angular/core';
import { FormArray, FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { DateAdapter } from '@angular/material/core';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { DestinosService } from './diarias-destinos.service';
import moment from 'moment';
import { apiVeiculoMotoristaDaaCriar, Payload } from 'api/diarias/analise-beneficiario/api-analise-daa-veicuo-motorista-criar.service';
import { apiDiariasMotoristasService } from 'api/diarias/api-diarias-motoristas.service';
import { NovoDadosBancariosComponent } from 'apps/vdf/minhas-diarias/novo-dados-bancarios/novo-dados-bancarios.component';
import { DatePipe } from '@angular/common';

interface VeiculoForm {
    capacidade_passageiros: FormControl<number | null>;
    marca: FormControl<string>;
    modelo: FormControl<string>;
    placa: FormControl<string>;
}

interface MotoristaForm {
    motorista: FormControl<number | null>;
}

class DaaCriarMotoristaVeiculoData {
    destinoId: number;
    viagemID: number;
    comMotorista: boolean;
    veiculoDaa: boolean;
    onClose?: Function;
}

@Component({
    selector: 'daa-motorista-veiculo-criar',
    templateUrl: 'daa-motorista-veiculo-criar.component.html',
    providers: [DatePipe],
    standalone: false
})

export class DaaCriarMotoristaVeiculoComponent extends MpmtFormularioComponent<DaaCriarMotoristaVeiculoData> implements OnInit {
    filtros = new FormGroup({
        palavra_chave: new FormControl<string>('', [])
    });

    servidores: any[] = [];
    destinos: any[] = [];
    beneficiarios: any[] = [];
    motoristas: any[] = [];
    contaSelecionada: any = null;
    destinosDistintos: any[] = [];
    exibirBotaoSelecionarDadosBancarios = false;

    formularioVeiculo: FormGroup<VeiculoForm>;
    formularioMotorista: FormGroup<MotoristaForm>;
    formularioDestinosDistintos: FormArray;
    
    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: DaaCriarMotoristaVeiculoData,
        protected dialogRef: MatDialogRef<DaaCriarMotoristaVeiculoData>,
        protected snackBar: MatSnackBar,
        protected dateAdapter: DateAdapter<Date>,
        protected service: DestinosService,
        public dialog: MatDialog,
        private fb: FormBuilder
    ) {
        super(data, snackBar, dialogRef);
        this.dateAdapter.setLocale('pt-BR');
        this.formularioVeiculo = new FormGroup<VeiculoForm>({} as VeiculoForm);
        this.formularioMotorista = new FormGroup<MotoristaForm>({} as MotoristaForm);
    }

    async ngOnInit() {
        this.service.viagemID = this.data?.viagemID;
        this.service.comMotorista = this.data?.comMotorista;
        this.service.veiculoDaa = this.data?.veiculoDaa;

        this.montarFormulario();

        this.configurarColunas();
        await this.service.recarregarListagem();
        this.preSelecionarDestino();

        await this.carregarMotoristas();

        this.service.destinosDistintos$.subscribe((destinos) => {
            this.initDestinosFormArray(destinos);
        });
    }

    private montarFormulario() {
        if (this.data.veiculoDaa) {
            this.formularioVeiculo = new FormGroup<VeiculoForm>({
                capacidade_passageiros: new FormControl<number | null>(null, [Validators.required]),
                marca: new FormControl<string>('', [Validators.required]),
                modelo: new FormControl<string>('', [Validators.required]),
                placa: new FormControl<string>('', [Validators.required]),
            });
        }

        if (this.data.comMotorista) {
            this.formularioMotorista = new FormGroup<MotoristaForm>({
                motorista: new FormControl<number | null>(null, [Validators.required]),
            });
        }

        this.formularioDestinosDistintos = this.fb.array([]);
        this.service.destinosDistintos$.subscribe((destinos) => {
            this.initDestinosFormArray(destinos);
        });
    }

    private initDestinosFormArray(destinos: any[]) {
        this.formularioDestinosDistintos.clear();
        destinos.forEach(destino => {
            const destinoGroup = this.fb.group({
                ids: [destino.ids],
                origem: `${destino.uf_origem_sigla} / ${destino.municipio_origem_display}`,
                destino: `${destino.uf_destino_sigla} / ${destino.municipio_destino_display}`,
                data: [this.formatarData(destino.data), Validators.required],
                hora: [this.obterHora(destino.data), Validators.required]
            });
            this.formularioDestinosDistintos.push(destinoGroup);
        });
    }

    protected async preSelecionarDestino() {
        try {
            this.service.listagem$.subscribe((itens) => {
                const destinoSelecionado = itens.find(item => item.id === this.data.destinoId);
                if (destinoSelecionado) {
                    this.service.adicionarItemSelecionado(destinoSelecionado);
                }
            });
        } catch (error) {
            console.error('Erro ao pré-selecionar o destino:', error);
        }
    }

    protected async carregarMotoristas() {
        try {
            const respostaMotoristas = await apiDiariasMotoristasService({});
            this.motoristas = respostaMotoristas.results;
        } catch (error) {
            console.error('Erro ao carregar motoristas:', error);
            this.exibirMensagem('Erro', 'Não foi possível carregar a lista de motoristas.');
        }
    }

    abrirModalDadosBancarios() {
        const dialogRef = this.dialog.open(NovoDadosBancariosComponent, {
            data: { 
                servidor_id: this.formularioMotorista.value.motorista,
                beneficiario_id: null,
                contaSelecionada: this.contaSelecionada,
            }
        });

        dialogRef.afterClosed().subscribe(result => {
            if (result && result.conta) {
                this.contaSelecionada = result.conta;
            }
        });
    }

    onMotoristaChange() {
        const motoristaSelecionado = this.formularioMotorista.value.motorista;
        if (motoristaSelecionado) {
            this.exibirBotaoSelecionarDadosBancarios = true;
            this.contaSelecionada = null;
        } else {
            this.exibirBotaoSelecionarDadosBancarios = false; 
        }
    }

    private configurarColunas() {
        this.service.configurarColunas([
            {
                codigo: 'checkbox',
                titulo: '',
                visivel: true,
                tipo: 'CHECKBOX',
                ordenavel: false,
            },
            {
                codigo: 'beneficiario_unicode',
                titulo: 'Beneficiário',
                visivel: true,
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
        ]);
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        if (!this.validarCapacidadeVeiculo()) return;

        if (this.data.comMotorista && !this.contaSelecionada) {
            this.exibirMensagem('Erro', 'Por favor, selecione os dados bancários para o motorista.');
            return;
        }

        const veiculoData = this.formularioVeiculo.value;
        const motoristaData = {
            motorista: this.formularioMotorista.value.motorista,
            conta_bancaria_pgto: this.contaSelecionada
        };

        const destinosData = this.formularioDestinosDistintos.value.map(destino => {
            const data = destino.data;
            const hora = destino.hora;
            const dataHora = `${data}T${hora}:00`;
            return { ids: destino.ids, dataHora: dataHora };
        });

        const payload: Payload = {
            veiculo: {
                placa: veiculoData.placa,
                marca: veiculoData.marca,
                modelo: veiculoData.modelo,
                capacidade_passageiros: veiculoData.capacidade_passageiros,
            },
            motorista: motoristaData,
            destinos: destinosData,
        };

        try {
            const response = await apiVeiculoMotoristaDaaCriar(payload);
            this.fecharFormulario();
            this.data?.onClose();
        } catch (e: any) {
            console.error(e);
            this.exibirMensagem('Erro', 'Não foi possível realizar a operação.');
        }
    }

    protected validarCapacidadeVeiculo(): boolean {
        const destinosSelecionados = this.service.obterItensSelecionados();
        const beneficiariosSelecionados = destinosSelecionados.map(destino => destino.beneficiario);

        const beneficiariosUnicos = new Set(beneficiariosSelecionados);
        const quantidadeBeneficiarios = beneficiariosUnicos.size;

        const capacidadeVeiculo = this.formularioVeiculo.value.capacidade_passageiros;

        const capacidadeDisponivelParaBeneficiarios = capacidadeVeiculo - 1;

        if (quantidadeBeneficiarios > capacidadeDisponivelParaBeneficiarios) {
            this.exibirMensagem(
                'Erro',
                `A capacidade do veículo é menor do que a quantidade de beneficiários selecionados. O veículo pode acomodar no máximo ${capacidadeDisponivelParaBeneficiarios} beneficiários.`
            );
            return false;
        }
        return true;
    }

    formatarData(data: string): string {
        return moment(data).format('YYYY-MM-DD');
    }

    obterHora(data: string): string {
        return moment(data).format('HH:mm');
    }

    atualizarDataHora(destino: any, novaData: string, novaHora: string) {
        const novaDataHora = moment(`${novaData}T${novaHora}`).toISOString();
        destino.data = novaDataHora;
    }

    protected fecharFormulario() {
        this.service.limparItensSelecionados();
        this.dialogRef.close();
    }

    get formularioValido(): boolean {
        const destinosSelecionados = this.service.obterItensSelecionados();
        return this.formularioVeiculo.valid && this.formularioMotorista.valid && destinosSelecionados.length > 0;
    }

    protected exibirMensagem(titulo: string, mensagem: string) {
        this.snackBar.open(mensagem, titulo, { duration: 3000 });
    }
}
