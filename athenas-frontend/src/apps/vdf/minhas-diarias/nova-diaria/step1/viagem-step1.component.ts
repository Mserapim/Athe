import { Component, ViewChild } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { apiDiariasChoicesFinalidades } from 'api/diarias/choices/api-diarias-finalidades.service';
import { apiDiariasChoicesMotivosViagem } from 'api/diarias/choices/api-diarias-motivos-viagem.service';

import { MpmtFileUpdateComponent } from 'components/mpmt-file-update/mpmt-file-update.component';
import { apiDiariasViagemCriar } from 'api/diarias/api-diarias-nova-viagem.service-criar';
import { MatSnackBar } from '@angular/material/snack-bar';
import { DiariaStepperService } from '../../stepper/diaria-stepper.service';
import { apiDiariasViagem } from 'api/diarias/api-diarias-viagem.service';
import { apiDiariasViagemEditar } from 'api/diarias/api-diarias-nova-viagem-editar.service';

import { Documento } from 'components/mpmt-file-update/mpmt-file-update.component';
import { map, Observable, startWith } from 'rxjs';
import { DateAdapter } from '@angular/material/core';
import moment from 'moment';


@Component({
    selector: 'viagem-step1',
    templateUrl: './viagem-step1.component.html',
    styleUrls: ['./viagem-step1.component.scss'],
    standalone: false
})
export class NovaDiariaStep1Component {

    titulo = 'Viagem';

    public finalidades: { descricao: string; id: number }[] = [];
    public motivos: { descricao: string; id: number }[] = [];

    finalidadesFiltradas: Observable<{ descricao: string; id: number }[]>;

    anexos: any[] = []
    anexos_carregados: Documento[] = []

    loading = false; // Variável de controle para o estado de carregamento

    @ViewChild('fileUpdate') fileUpdate: MpmtFileUpdateComponent;

    protected formulario = new FormGroup({
        tipo_viagem: new FormControl<string>('', [Validators.required]),
        hospedagem_anfitriao: new FormControl<boolean>(null, [Validators.required]),
        motivo_viagem: new FormControl<number>(null, [Validators.required]),
        finalidade_viagem: new FormControl<number | { descricao: string; id: number }>(null, [Validators.required]),
        data_inicio_viagem: new FormControl<string | null>(null, [Validators.required]),
        data_fim_viagem: new FormControl<string | null>(null, [Validators.required]),
        resumo: new FormControl<string>('', [Validators.required]),
        justificativa: new FormControl<string>('', [Validators.required]),
    });


    ngOnInit() {
        this.carregarDados();
        this.loadFinalidades();
        this.loadMotivos();
    }

    async carregarDados() {
        if (this.stepperService.id_viagem != null) {
            const results = await apiDiariasViagem({
                id: this.stepperService.id_viagem
            });
            const finalidade = this.finalidades.find(option => option.id === results.finalidade_viagem);

            this.formulario.get('tipo_viagem')?.setValue(results.tipo_viagem);
            this.formulario.get('hospedagem_anfitriao')?.setValue(results.hospedagem_anfitriao);
            this.formulario.get('motivo_viagem')?.setValue(results.motivo_viagem);
            this.formulario.get('finalidade_viagem')?.setValue(finalidade ? finalidade : results.finalidade_viagem);
            this.formulario.get('data_inicio_viagem')?.setValue(results.data_inicio_viagem);
            this.formulario.get('data_fim_viagem')?.setValue(results.data_fim_viagem);
            this.formulario.get('resumo')?.setValue(results.resumo);
            this.formulario.get('justificativa')?.setValue(results.justificativa);


            this.anexos_carregados = results.anexos.map((anexo: any) => {
                return {
                    id: anexo.id,
                    description: anexo.filename, 
                    name: anexo.filename, 
                    attachment_id: anexo.id,
                    originalName: anexo.filename 
                };
            });

        }

    }

    async loadFinalidades() {
        const { results } = await apiDiariasChoicesFinalidades({
            page: 1,
            per_page: 30,
        });
        this.finalidades = results;
        this.finalidadesFiltradas = this.formulario.get('finalidade_viagem')!.valueChanges.pipe(
            startWith(''),
            map(value => this.filterFinalidades(this.getFinalidadeDescricao(value)))
        );
    }

    private getFinalidadeDescricao(value: number | { descricao: string; id: number } | string): string {
        if (typeof value === 'number') {
          const finalidade = this.finalidades.find(option => option.id === value);
          return finalidade ? finalidade.descricao : '';
        } else if (typeof value === 'string') {
          return value;
        } else {
          return value?.descricao || '';
        }
    }

    private filterFinalidades(value: string | { descricao: string; id: number }): { descricao: string; id: number }[] {
        const filterValue = typeof value === 'string' ? value.toLowerCase() : value.descricao.toLowerCase();
        return this.finalidades.filter(option => option.descricao.toLowerCase().includes(filterValue));
    }
    
    displayFinalidade(finalidade: { descricao: string; id: number } | number): string {
        if (typeof finalidade === 'number') {
          const found = this.finalidades.find(option => option.id === finalidade);
          return found ? found.descricao : '';
        }
        return finalidade ? finalidade.descricao : '';
    }

    async loadMotivos() {
        const { results } = await apiDiariasChoicesMotivosViagem({
            page: 1,
            per_page: 30,
        });
        this.motivos = results;
    }


    constructor(
        private stepperService: DiariaStepperService,
        private _formBuilder: FormBuilder,
        private router: Router,
        protected snackBar: MatSnackBar,
        protected dateAdapter: DateAdapter<Date>,
    ) {
        stepperService.currentStep = 0;
        this.dateAdapter.setLocale('pt-BR');
    }

    get isValid() {
        return true;
    }

    async irProximo(): Promise<void> {

        if (!this.validarAvanco()) return null;

        if (this.stepperService.id_viagem){
            this.loading = true; // Exibe o spinner
        }
        

        const resposta = await this.salvarDados();

        if (resposta) {
            this.router.navigate(['vdf/minhas-diarias/nova/diaria', 'step2']);
        }

        this.loading = false; // Esconde o spinner
    }

    protected async salvarRascunho() {
        var resposta = this.salvarDados();
        if (resposta) {

            this.router.navigate(['vdf/minhas-diarias/']);
        }
    }

    protected async salvarDados() {
        if (!this.formulario.valid) return false;
        
        this.formulario.controls.data_inicio_viagem.setValue(moment(this.formulario.controls.data_inicio_viagem.value).format('YYYY-MM-DD'))
        this.formulario.controls.data_fim_viagem.setValue(moment(this.formulario.controls.data_fim_viagem.value).format('YYYY-MM-DD'))

        const { tipo_viagem, hospedagem_anfitriao, motivo_viagem, finalidade_viagem, data_inicio_viagem, data_fim_viagem, resumo, justificativa } = this.formulario.value;
        const anexos = this.anexos

        try {

            if (this.stepperService.id_viagem == null) {

                const { id } = await apiDiariasViagemCriar
                    ({
                        tipo_viagem,
                        hospedagem_anfitriao,
                        motivo_viagem,
                        finalidade_viagem: (finalidade_viagem as { descricao: string; id: number }).id,
                        data_inicio_viagem,
                        data_fim_viagem,
                        resumo,
                        justificativa,
                        anexos
                    });

                this.stepperService.id_viagem = id;
            } else {

                const { } = await apiDiariasViagemEditar
                    ({
                        id: this.stepperService.id_viagem,
                        tipo_viagem,
                        hospedagem_anfitriao,
                        motivo_viagem,
                        finalidade_viagem: (finalidade_viagem as { descricao: string; id: number }).id,
                        data_inicio_viagem,
                        data_fim_viagem,
                        resumo,
                        justificativa,
                        anexos
                    });
            }

            return true;
        } catch (e: any) {
            console.error(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao salvar rascunho. ${detalheErro}`;
            this.exibirMensagem('Aviso', texto);
            return false;
        }
    }

    tipos_viagem = [
        { id: 'ESTADUAL', descricao: 'Estadual' },
        { id: 'NACIONAL', descricao: 'Nacional' },
        { id: 'INTERNACIONAL', descricao: 'Internacional' },
    ];

    protected async receberAnexos(dados: []) {
        this.anexos = dados
    }

    protected exibirMensagem(titulo: string, texto: string) {
        this.snackBar.open(texto, '', {
            duration: 10000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: ['custom-snackbar']
        });
    }

    validarAvanco(): boolean{
        let resposta = true
        if (!this.formulario.valid) resposta = false;

        if(this.anexos.length == 0) resposta = false;

        if(!resposta){
            this.exibirMensagem('Aviso','Preencha todos os campos do formulário.')
        }

        return resposta;
    }
}
