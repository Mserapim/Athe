import { Component, Inject, OnInit } from '@angular/core';
import { FormArray, FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiDiariasConfigCondicionais } from 'api/diarias/config/api-diarias-config-condicionais.service';
import { apiDiariasConfigEtapas } from 'api/diarias/config/api-diarias-config-etapas.service';
import { apiDiariasConfigFluxoCriar } from 'api/diarias/config/api-diarias-config-fluxo-criar.service';
import { apiDiariasConfigSituacoes } from 'api/diarias/config/api-diarias-config-situacoes.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { CondicionaisExplicacaoModalComponent } from './tutorial-condicionais/condicionais-explicacao.component';

class DiariasConfigFluxoNovoComponentData {
    onClose?: Function;
}

@Component({
    selector: 'diarias-config-fluxo-novo',
    templateUrl: 'diarias-config-fluxo-novo.component.html',
    standalone: false
})
export class DiariasConfigFluxoNovoComponent extends MpmtFormularioComponent<DiariasConfigFluxoNovoComponentData> implements OnInit{
    etapas: any[] = [];
    situacoes: any[] = [];
    condicionais: any[] = [];

    formulario: FormGroup;

    ngOnInit() {
        super.ngOnInit();
        this.carregarEtapas();
        this.carregarSituacoes();
        this.carregarCondicionais();
    }

    constructor(
        private fb: FormBuilder,
        @Inject(MAT_DIALOG_DATA)
        protected data: DiariasConfigFluxoNovoComponentData,
        protected dialogRef: MatDialogRef<DiariasConfigFluxoNovoComponentData>,
        protected snackBar: MatSnackBar,
        private dialog: MatDialog
    ) {
        super(data, snackBar, dialogRef);
        this.formulario = this.fb.group({
            etapa: ['', Validators.required],
            ordem: [0, Validators.required],
            situacao: ['', Validators.required],
            link_informacao: [''],
            grupos_condicionais: this.fb.array([]),
            notificar_solicitante: [false],
            deferir_todos_beneficiarios: [false],
            calcular: [false],
        });

        this.adicionarGrupoCondicional();
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { etapa, ordem, situacao, link_informacao, notificar_solicitante, grupos_condicionais, calcular, deferir_todos_beneficiarios } = this.formulario.value;

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
            const {} = await apiDiariasConfigFluxoCriar({
                etapa,
                ordem,
                situacao,
                link_informacao,
                notificar_solicitante,
                condicionais,
                calcular,
                deferir_todos_beneficiarios
            });

            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose();
        } catch (e: any) {
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao salvar o módulo. ${detalheErro}`;
            this.exibirMensagem('Atenção', texto);
        }
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

    criarGrupoCondicional(): FormGroup {
        return this.fb.group({
            operador_entre_grupos: [null],
            condicionais: this.fb.array([this.criarCondicional()])
        });
    }

    criarCondicional(): FormGroup {
        return this.fb.group({
            condicao: [''],
            operador: [null] 
        });
    }

    get gruposCondicionais(): FormArray {
        return this.formulario.get('grupos_condicionais') as FormArray;
    }

    adicionarGrupoCondicional() {
        this.gruposCondicionais.push(this.criarGrupoCondicional());
    }

    removerGrupoCondicional(groupIndex: number) {
        this.gruposCondicionais.removeAt(groupIndex);
    }

    adicionarCondicional(groupIndex: number) {
        const grupo = this.gruposCondicionais.at(groupIndex).get('condicionais') as FormArray;

        // Verificar o operador da segunda condicional em diante
        let operadorAtual = grupo.length > 1 ? grupo.at(1)?.get('operador')?.value : null;

        // A primeira condiconal do grupo não precisa de operador
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

    grupoCondicionaisValido(groupIndex: number): boolean {
        const grupo = this.gruposCondicionais.at(groupIndex).get('condicionais') as FormArray;
        return grupo.controls.every((cond, condIndex) => {
            const condicaoValida = !!cond.get('condicao')?.value;  
            const operadorValido = condIndex === 0 || cond.get('operador')?.value !== null;  
            return condicaoValida && operadorValido;
        });
    }

    todosGruposCondicionaisValidos(): boolean {
        return this.gruposCondicionais.controls.every((grupo, groupIndex) => {
            const operadorEntreGruposValido = groupIndex === 0 || !!grupo.get('operador_entre_grupos')?.value;  // Verificar se o operador entre grupos está preenchido
            return this.grupoCondicionaisValido(groupIndex) && operadorEntreGruposValido;
        });
    }

    podeAdicionarCondicional(groupIndex: number): boolean {
        return this.grupoCondicionaisValido(groupIndex);
    }

    podeAdicionarGrupo(): boolean {
        return this.todosGruposCondicionaisValidos();
    }

    protected resetarFormulario() {
        while (this.gruposCondicionais.length !== 0) {
            this.gruposCondicionais.removeAt(0);
        }
        this.adicionarGrupoCondicional();
    
        this.formulario.reset({
            etapa: this.formularioPadrao.etapa,
            ordem: this.formularioPadrao.ordem,
            situacao: this.formularioPadrao.situacao,
            notificar_solicitante: this.formularioPadrao.notificar_solicitante,
            deferir_todos_beneficiarios: this.formularioPadrao.deferir_todos_beneficiarios,
            calcular: this.formularioPadrao.calcular
        });
    }

    abrirExplicacaoCondicionais() {
        const dialogRef = this.dialog.open(CondicionaisExplicacaoModalComponent, {
            width: '700px'
        });
    }
}
