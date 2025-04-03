import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiPainelControleControleAcessoModuloCriar } from 'api/painel-controle/api-painel-controle-controle-acesso-modulo-criar.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import {ModalButton} from "../../../layout/mpmt-modal/layout-padrao-modal.component";
import {CoresPadraoEnum} from "../../../enums/CoresPadraoEnum";

class PainelControleModuloNovoComponentData {
    onClose?: Function;
}

@Component({
    selector: 'painel-controle-modulo-novo',
    templateUrl: 'painel-controle-modulo-novo.component.html',
    standalone: false
})
export class PainelControleModuloNovoComponent extends MpmtFormularioComponent<PainelControleModuloNovoComponentData> {

    selectedIcon: string;

    modalButtons: ModalButton[] = [
        {
            label: 'Salvar',
            action: () => this.confirmarFormulario(),
            disabled: () => !this.formularioValido,
            color: 'white',
            backgroundColor: CoresPadraoEnum.verde
        }
    ];

    protected formulario = new FormGroup({
        nome: new FormControl<string>('', [Validators.required]),
        descricao: new FormControl<string>(''),
        sigla: new FormControl<string>('', [Validators.required]),
        icone: new FormControl<string>('', [Validators.required]),
        ordem: new FormControl<number>(0, [Validators.required]),
        situacao: new FormControl<'ATIVO' | 'INATIVO'>('ATIVO', [
            Validators.required,
        ]),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: PainelControleModuloNovoComponentData,
        protected dialogRef: MatDialogRef<PainelControleModuloNovoComponentData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    onIconSelected($event) {
        this.formulario.controls.icone.setValue($event);
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { nome, descricao, ordem, sigla, icone , situacao } = this.formulario.value;

        try {
            const {} = await apiPainelControleControleAcessoModuloCriar({
                nome,
                descricao,
                ordem,
                sigla,
                icone,
                situacao,
            });

            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose();
        } catch (e: any) {
            console.log(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao salvar o módulo. ${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }
    }

    situacoes = [
        { valor: 'ATIVO', nome: 'Ativo' },
        { valor: 'INATIVO', nome: 'Inativo' },
    ];
}
