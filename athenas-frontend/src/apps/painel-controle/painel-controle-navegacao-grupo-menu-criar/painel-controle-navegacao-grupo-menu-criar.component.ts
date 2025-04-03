import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiPainelControleControleAcessoGrupoMenuCriar } from 'api/painel-controle/api-painel-controle-controle-acesso-grupo-menu-criar.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { CoresPadraoEnum } from 'enums/CoresPadraoEnum';
import { ModalButton } from 'layout/mpmt-modal/layout-padrao-modal.component';

class PainelControleNavegacaoGrupoMenuCriarComponentData {
    onClose?: Function;
    modulo: number;
}

@Component({
    selector: 'painel-controle-navegacao-grupo-menu-criar',
    templateUrl: 'painel-controle-navegacao-grupo-menu-criar.component.html',
    standalone: false
})
export class PainelControleNavegacaoGrupoMenuCriarComponent extends MpmtFormularioComponent<PainelControleNavegacaoGrupoMenuCriarComponentData> {

    selectedIcon: string;

    protected formulario = new FormGroup({
        nome: new FormControl<string>('', [Validators.required]),
        descricao: new FormControl<string>(''),
        icone: new FormControl<string>('', [Validators.required]),
        ordem: new FormControl<number>(0, [Validators.required]),
        situacao: new FormControl<'ATIVO' | 'INATIVO'>('ATIVO', [
            Validators.required,
        ]),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: PainelControleNavegacaoGrupoMenuCriarComponentData,
        protected dialogRef: MatDialogRef<PainelControleNavegacaoGrupoMenuCriarComponentData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
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

    controlarTitulo() {
        return 'Novo Grupo de Menu'
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { nome, descricao, icone, ordem, situacao } = this.formulario.value;

        try {
            const {} = await apiPainelControleControleAcessoGrupoMenuCriar({
                modulo: this.data.modulo,
                nome,
                descricao,
                icone,
                ordem,
                situacao,
            });

            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose();
        } catch (e: any) {
            this.exibirErro(e);
        }
    }

    situacoes = [
        { valor: 'ATIVO', nome: 'Ativo' },
        { valor: 'INATIVO', nome: 'Inativo' },
    ];

    onIconSelected($event) {
        this.formulario.controls.icone.setValue($event);
    }
}
