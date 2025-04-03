import { Component, Inject, ViewChild } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { DateAdapter } from '@angular/material/core';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiPainelControleServicoCriar } from 'api/painel-controle/api-painel-controle-servico-criar.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { ModalClasscodesComponent } from '../classcodes/modal-classcodes/modal-classcodes.component';
import { apiPainelControleClasscodes } from 'api/painel-controle/api-painel-controle-classcodes.service';
import { MpmtSelecaoFormComponent, MpmtSelecaoFormComponentConfiguracao } from 'components/mpmt-selecao-form/mpmt-selecao-form.component';
import { ModalButton } from 'layout/mpmt-modal/layout-padrao-modal.component';
import { CoresPadraoEnum } from 'enums/CoresPadraoEnum';

class PainelControleServicoNovoComponentData {
    onClose?: Function;
}

@Component({
    selector: 'painel-controle-servico-novo',
    templateUrl: 'painel-controle-servico-novo.component.html',
    standalone: false
})
export class PainelControleServicoNovoComponent extends MpmtFormularioComponent<PainelControleServicoNovoComponentData> {
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
        protected data: PainelControleServicoNovoComponentData,
        protected dialogRef: MatDialogRef<PainelControleServicoNovoComponentData>,
        protected snackBar: MatSnackBar,
        protected dateAdapter: DateAdapter<Date>,
        public dialog: MatDialog,
    ) {
        super(data, snackBar, dialogRef);
        this.dateAdapter.setLocale('pt-BR');
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
            width: '80%',
            height: '90%',
        });
    };

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

    controlarTitulo() {
        return 'Novo Serviço'
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


    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { name, command, description, classcode } = this.formulario.value;

        try {
            const {} = await apiPainelControleServicoCriar({
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
            const texto = `Ocorreu um erro inesperado ao salvar o serviço. ${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }
    }
}
