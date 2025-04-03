import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiPainelControleControleAcessoMenuCriar } from 'api/painel-controle/api-painel-controle-controle-acesso-menu-criar.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { CoresPadraoEnum } from 'enums/CoresPadraoEnum';
import { ModalButton } from 'layout/mpmt-modal/layout-padrao-modal.component';

export class PainelControleNavegacaoMenuCriarComponentData {
    onClose?: Function;
    grupoMenuId: number;
}

@Component({
    selector: 'painel-controle-navegacao-menu-criar',
    templateUrl: 'painel-controle-navegacao-menu-criar.component.html',
    standalone: false
})
export class PainelControleNavegacaoMenuCriarComponent extends MpmtFormularioComponent<PainelControleNavegacaoMenuCriarComponentData> {

    selectedIcon: string;

    protected formulario = new FormGroup({
        nome: new FormControl<string>('', [Validators.required]),
        descricao: new FormControl<string>(''),
        icone: new FormControl<string>('', [Validators.required]),
        ordem: new FormControl<number>(0, [Validators.required]),
        url: new FormControl<string>('', [Validators.required]),
        link_de_ajuda: new FormControl<string>(''),
        situacao: new FormControl<'ATIVO' | 'INATIVO'>('ATIVO', [
            Validators.required,
        ]),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: PainelControleNavegacaoMenuCriarComponentData,
        protected dialogRef: MatDialogRef<PainelControleNavegacaoMenuCriarComponentData>,
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
        return 'Novo Menu'
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { nome, descricao, ordem, icone, url, link_de_ajuda } = this.formulario.value;

        try {
            const {} = await apiPainelControleControleAcessoMenuCriar({
                grupo: this.data.grupoMenuId,
                situacao: 'ATIVO',
                icone,
                nome,
                descricao,
                ordem,
                url,
                link_de_ajuda,
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
