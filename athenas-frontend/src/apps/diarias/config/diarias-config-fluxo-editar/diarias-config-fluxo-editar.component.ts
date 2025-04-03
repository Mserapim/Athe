import { Component, Inject, OnInit } from '@angular/core';
import { FormArray, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiDiariasConfigCondicionais } from 'api/diarias/config/api-diarias-config-condicionais.service';
import { apiDiariasConfigEtapas } from 'api/diarias/config/api-diarias-config-etapas.service';
import { apiDiariasConfigFluxoEditar } from 'api/diarias/config/api-diarias-config-fluxo-editar.service';
import { apiDiariasConfigFluxo } from 'api/diarias/config/api-diarias-config-fluxo.service';
import { apiDiariasConfigSituacoes } from 'api/diarias/config/api-diarias-config-situacoes.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { CondicionaisExplicacaoModalComponent } from '../diarias-config-fluxo-novo/tutorial-condicionais/condicionais-explicacao.component';

class DiariasConfigFluxoEditarComponentData {
    pk: number;
    onClose?: Function;
}

@Component({
    selector: 'diarias-config-fluxo-editar',
    templateUrl: 'diarias-config-fluxo-editar.component.html',
    standalone: false
})
export class DiariasConfigFluxoEditarComponent extends MpmtFormularioComponent<DiariasConfigFluxoEditarComponentData> implements OnInit{
    etapas: any[] = [];
    situacoes: any[] = [];
    condicionais: any[] = [];

    formulario: FormGroup;

    ngOnInit() {
        super.ngOnInit();
        this.carregarCondicionais().then(() => {
            this.carregarEtapas();
            this.carregarSituacoes();
            this.carregarDadosDoFluxo();
        });
    }

    constructor(
        private fb: FormBuilder,
        @Inject(MAT_DIALOG_DATA)
        protected data: DiariasConfigFluxoEditarComponentData,
        protected dialogRef: MatDialogRef<DiariasConfigFluxoEditarComponentData>,
        protected snackBar: MatSnackBar,
        private dialog: MatDialog
    ) {
        super(data, snackBar, dialogRef);
        this.formulario = this.fb.group({
            id: [null, Validators.required],
            etapa: ['', Validators.required],
            ordem: [0, Validators.required],
            situacao: ['', Validators.required],
            link_informacao: [''],
            grupos_condicionais: this.fb.array([]),
            notificar_solicitante: [false],
            deferir_todos_beneficiarios: [false],
            calcular: [false],
        });
    }

    async carregarDadosDoFluxo() {
        try {
            const { id, ordem, etapa, situacao, link_informacao, notificar_solicitante, condicionais, calcular, deferir_todos_beneficiarios } =
                await apiDiariasConfigFluxo({ id: this.data.pk });

            this.formulario.patchValue({
                id,
                ordem,
                etapa,
                situacao,
                link_informacao,
                notificar_solicitante,
                calcular,
                deferir_todos_beneficiarios,
            });

            this.carregarCondicionaisDoFluxo(condicionais);
        } catch (e) {
            console.error('Erro ao carregar dados do fluxo:', e);
            this.exibirMensagem('Erro', 'Não foi possível carregar os dados do fluxo.');
        }
    }

    carregarCondicionaisDoFluxo(condicionais: any[]) {
        if (!this.condicionais || this.condicionais.length === 0) {
            console.error("Lista de condicionais ainda não carregada.");
            return;
        }
    
        this.gruposCondicionais.clear();
    
        condicionais.forEach((cond: any, index: number) => {
            if (cond.condicionais) {
                let tipo_operador_condicional: string | null = null;
                if (cond.condicionais.includes(',')) {
                    tipo_operador_condicional = 'OU';
                } else if (cond.condicionais.includes(';')) {
                    tipo_operador_condicional = 'E';
                }

                const operadorEntreGrupos = cond.tipo_operador || null;
        
                const idsCondicionais = cond.condicionais.split(tipo_operador_condicional === 'OU' ? ',' : ';');
        
                const grupo = this.fb.group({
                    operador_entre_grupos: [operadorEntreGrupos],
                    condicionais: this.fb.array([]),
                });
        
                idsCondicionais.forEach((id: string, i: number) => {
                    const operador = i === 0 ? null : tipo_operador_condicional;
                    
                    (grupo.get('condicionais') as FormArray).push(
                        this.fb.group({
                            condicao: [parseInt(id.trim(), 10)],
                            operador: [operador],
                        })
                    );
                });
                this.gruposCondicionais.push(grupo);
            }
        });
    }
 
    async carregarEtapas() {
        try {
            this.etapas = await apiDiariasConfigEtapas({});
        } catch (error) {
            console.error('Erro ao carregar as etapas:', error);
            this.exibirMensagem('Erro', 'Não foi possível carregar as etapas');
        }
    }

    async carregarSituacoes() {
        try {
            this.situacoes = await apiDiariasConfigSituacoes({});
        } catch (error) {
            console.error('Erro ao carregar as situacoes:', error);
            this.exibirMensagem('Erro', 'Não foi possível carregar as situacoes');
        }
    }

    async carregarCondicionais() {
        try {
            this.condicionais = await apiDiariasConfigCondicionais({});
        } catch (error) {
            console.error('Erro ao carregar as condicionais:', error);
            this.exibirMensagem('Erro', 'Não foi possível carregar as condicionais');
        }
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { id, etapa, ordem, situacao, link_informacao, notificar_solicitante, grupos_condicionais, calcular, deferir_todos_beneficiarios } = this.formulario.value;

        const condicionais = grupos_condicionais.map((grupo: any) => {
            let idsCondicionais = grupo.condicionais
            .map((cond: any) => cond.condicao)
            .join(grupo.condicionais[1]?.operador === 'OU' ? ',' : ';');

            idsCondicionais = idsCondicionais.replace(/[;,]$/, '');

            if (idsCondicionais === 'NaN' || idsCondicionais === '') {
                idsCondicionais = null;
            }

            return {
                tipo_operador: grupo.operador_entre_grupos || null,
                ids_condicionais: idsCondicionais,
            };
        });

        try {
            const {} = await apiDiariasConfigFluxoEditar({
                id,
                etapa,
                ordem,
                situacao,
                link_informacao,
                notificar_solicitante,
                condicionais,
                calcular,
                deferir_todos_beneficiarios,
            });

            this.fecharFormulario();
            this.data?.onClose();
        } catch (error) {
            const detalheErro = error?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao salvar o fluxo. ${detalheErro}`;
            this.exibirMensagem('Erro', texto);
        }
    }

    get gruposCondicionais(): FormArray {
        return this.formulario.get('grupos_condicionais') as FormArray;
    }

    criarGrupoCondicional(): FormGroup {
        return this.fb.group({
            operador_entre_grupos: [null],
            condicionais: this.fb.array([this.criarCondicional()]),
        });
    }

    criarCondicional(): FormGroup {
        return this.fb.group({
            condicao: [''],
            operador: [null],
        });
    }

    adicionarGrupoCondicional() {
        this.gruposCondicionais.push(this.criarGrupoCondicional());
    }

    removerGrupoCondicional(groupIndex: number) {
        this.gruposCondicionais.removeAt(groupIndex);
    }

    adicionarCondicional(groupIndex: number) {
        //Pela regra definida, cada grupo de condicional pode conter somente um tipo de operador (E ou OU)
        const grupo = this.gruposCondicionais.at(groupIndex).get('condicionais') as FormArray;

        // Verificar o operador da segunda condicional em diante
        let operadorAtual = grupo.length > 1 ? grupo.at(1)?.get('operador')?.value : null;

        // Se a condicional for a primeira do grupo, não precisa de operador
        if (grupo.length === 0 || grupo.length === 1) {
            grupo.push(this.fb.group({
                condicao: [''],
                operador: [null]
            }));
        } else {
            const operadorAtual = grupo.at(1)?.get('operador')?.value;
            grupo.push(this.fb.group({
                condicao: [''],
                operador: [{ value: operadorAtual, disabled: true }]  // As condicionais herdam o operador da primeira
            }));
        }
    }    

    removerCondicional(groupIndex: number, condIndex: number) {
        const grupo = this.gruposCondicionais.at(groupIndex).get('condicionais') as FormArray;
        grupo.removeAt(condIndex);
    }

    atualizarOperadores(groupIndex: number, operador: string) {
        const grupo = this.gruposCondicionais.at(groupIndex).get('condicionais') as FormArray;

        for (let i = 1; i < grupo.length; i++) {
            const condicional = grupo.at(i);
            condicional.get('operador')?.setValue(operador);
        }
    }

    todosGruposCondicionaisValidos(): boolean {
        return this.gruposCondicionais.controls.every((grupo, groupIndex) => {
            const operadorEntreGruposValido = groupIndex === 0 || !!grupo.get('operador_entre_grupos')?.value;
            return this.grupoCondicionaisValido(groupIndex) && operadorEntreGruposValido;
        });
    }

    grupoCondicionaisValido(groupIndex: number): boolean {
        const grupo = this.gruposCondicionais.at(groupIndex).get('condicionais') as FormArray;
        return grupo.controls.every((cond, condIndex) => {
            const condicaoValida = !!cond.get('condicao')?.value;
            const operadorValido = condIndex === 0 || cond.get('operador')?.value !== null;
            return condicaoValida && operadorValido;
        });
    }

    podeAdicionarGrupo(): boolean {
        return this.todosGruposCondicionaisValidos();
    }

    podeAdicionarCondicional(groupIndex: number): boolean {
        return this.grupoCondicionaisValido(groupIndex);
    }

    abrirExplicacaoCondicionais() {
        const dialogRef = this.dialog.open(CondicionaisExplicacaoModalComponent, {
            width: '700px'
        });
    }
}