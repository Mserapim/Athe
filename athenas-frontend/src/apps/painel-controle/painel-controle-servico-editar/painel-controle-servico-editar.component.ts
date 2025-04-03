import { Component, Inject, ViewChild } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { DateAdapter } from '@angular/material/core';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiPainelControleServicoEditar } from 'api/painel-controle/api-painel-controle-servico-editar.service';
import { apiPainelControleServico } from 'api/painel-controle/api-painel-controle-servico.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { MpmtSelecaoFormComponent, MpmtSelecaoFormComponentConfiguracao } from 'components/mpmt-selecao-form/mpmt-selecao-form.component';
import { ModalClasscodesComponent } from '../classcodes/modal-classcodes/modal-classcodes.component';
import { apiPainelControleClasscodes } from 'api/painel-controle/api-painel-controle-classcodes.service';
import { Bold, ClassicEditor, Essentials, Italic, Mention, Paragraph, Undo } from 'ckeditor5';
import { ModalButton } from 'layout/mpmt-modal/layout-padrao-modal.component';
import { CoresPadraoEnum } from 'enums/CoresPadraoEnum';

class PainelControleServicoEditarComponentData {
    servico_id: number;
    onClose?: Function;
}

@Component({
    selector: 'painel-controle-servico-editar',
    templateUrl: 'painel-controle-servico-editar.component.html',
    standalone: false
})
export class PainelControleServicoEditarComponent extends MpmtFormularioComponent<PainelControleServicoEditarComponentData> {
    @ViewChild('selecaoClasscode') selecaoClasscode: MpmtSelecaoFormComponent;

    private classcodeCarregado: number = null;

    protected formulario = new FormGroup({
        name: new FormControl<string>('', [Validators.required]),
        command: new FormControl<string>('', [Validators.required]),
        description: new FormControl<string>('', [Validators.required]),
        classcode: new FormControl<number>(null, [Validators.required]),
        classcode_path: new FormControl<string>('', []),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: PainelControleServicoEditarComponentData,
        protected dialogRef: MatDialogRef<PainelControleServicoEditarComponentData>,
        protected snackBar: MatSnackBar,
        protected dateAdapter: DateAdapter<Date>,
        public dialog: MatDialog,
    ) {
        super(data, snackBar, dialogRef);
        this.dateAdapter.setLocale('pt-BR');
    }

    public Editor = ClassicEditor;
    public config = {
        toolbar: ['undo', 'redo', '|', 'bold', 'italic'],
        plugins: [Bold, Essentials, Italic, Mention, Paragraph, Undo],
    };

    ngAfterViewInit() {
        this.carregarDados();
    }

    controlarTitulo() {
        return 'Editar Serviço'
    }

    modalButtons: ModalButton[] = [
        {
            label: 'Salvar',
            action: () => this.confirmarFormulario(),
            disabled: () => !this.formularioValido,
            color: 'white',
            backgroundColor: CoresPadraoEnum.verde
        }
    ];



    async carregarDados() {
        if (this.data.servico_id != null) {
            try {
                const response = await apiPainelControleServico({
                    id: this.data.servico_id,
                });

                this.classcodeCarregado = response.classcode
                this.selecaoClasscode.limparSelecao();

                await this.formulario.patchValue({
                    ...(response as any),
                });

            } catch (e) {
                console.error(e);
                this.exibirMensagem(
                    'Atenção',
                    'Erro inesperado ao carregar os valores do formulário'
                );
            }

        }
    }

    protected irNovoClasscode() {
        this.dialog.open(ModalClasscodesComponent, {
            data: {
                onClose: (classcode) => {
                    this.classcodeCarregado = classcode.id;

                    this.selecaoClasscode.limparSelecao();
                    
                    this.formulario.patchValue({
                        classcode: classcode.id,
                        classcode_path: classcode.path,
                    });
                },
            },
            width: '60%',
            height: '90%',
        });
    }

    protected irEditarClasscode() {
        this.dialog.open(ModalClasscodesComponent, {
            data: {
                selecionada: this.formulario.value.classcode,
                onClose: (classcode) => {
                    this.classcodeCarregado = classcode.id;

                    this.selecaoClasscode.limparSelecao();

                    this.formulario.patchValue({
                        classcode: classcode.id,
                        classcode_path: classcode.path,
                    });
                },
            },
            width: '80%',
            height: '90%',
        });
    }

    protected get classcodeSelecionado(): boolean {
        if (this.formulario?.value?.classcode == null) {
            return true
        }
        return false
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { name, command, description } = this.formulario.value;

        const classcode = this.selecaoClasscode.form_control.value;

        try {
            const {} = await apiPainelControleServicoEditar({
                id: this.data.servico_id,
                name: name,
                command: command,
                description: description,
                classcode: classcode,
            });

            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose();
        } catch (e: any) {
            console.log(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao editar o serviço. ${detalheErro}`;
            this.exibirMensagem('Atenção', texto);
        }
    }

    selecaoServicoClasscodes: MpmtSelecaoFormComponentConfiguracao = {
        obterOpcoes: apiPainelControleClasscodes,
        obterFiltros: (payload) => {
            return {
                ...payload,
                id: this.classcodeCarregado,
                per_page: 10,
            };
        },
        obterValor: 'id',
        obterTitulo: 'path',
    };
}
