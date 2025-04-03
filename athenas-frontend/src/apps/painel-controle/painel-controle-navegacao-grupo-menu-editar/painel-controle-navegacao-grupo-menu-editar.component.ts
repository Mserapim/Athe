import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiPainelControleControleAcessoGrupoMenuEditar } from 'api/painel-controle/api-painel-controle-controle-acesso-grupo-menu-editar.service';
import { apiPainelControleControleAcessoModuloGruposMenus } from 'api/painel-controle/api-painel-controle-controle-acesso-modulo-grupos-menus.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { CoresPadraoEnum } from 'enums/CoresPadraoEnum';
import { ModalButton } from 'layout/mpmt-modal/layout-padrao-modal.component';

class PainelControleNavegacaoGrupoMenuEditarComponentData {
    onClose?: Function;
    modulo: number;
    grupoMenuId: number;
}

@Component({
    selector: 'painel-controle-navegacao-grupo-menu-editar',
    templateUrl: 'painel-controle-navegacao-grupo-menu-editar.component.html',
    standalone: false
})
export class PainelControleNavegacaoGrupoMenuEditarComponent extends MpmtFormularioComponent<PainelControleNavegacaoGrupoMenuEditarComponentData> {
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

    ngOnInit() {
        super.ngOnInit();
        this.resetarFormulario()
    }

    grupoMenu = [];

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: PainelControleNavegacaoGrupoMenuEditarComponentData,
        protected dialogRef: MatDialogRef<PainelControleNavegacaoGrupoMenuEditarComponentData>,
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
        return 'Editar Grupo de Menu'
    }

    protected async resetarFormulario() {
        super.resetarFormulario();
        try {
            const { results: grupoMenu } =
                await  apiPainelControleControleAcessoModuloGruposMenus({
                    id: this.data.grupoMenuId,
                });

            this.grupoMenu = grupoMenu;
            if (this.grupoMenu.length > 0) {
                this.formulario.setValue({
                    nome: this.grupoMenu[0].nome,
                    descricao: this.grupoMenu[0].descricao,
                    icone: this.grupoMenu[0].icone,
                    ordem: this.grupoMenu[0].ordem,
                    situacao: this.grupoMenu[0].situacao
                });

                this.selectedIcon = this.grupoMenu[0].icone;
            }

        } catch (e) {
            console.log(e);
            this.exibirMensagem(
                'Atenção',
                'Erro inesperado ao carregar os valores do formulário'
            );
        }
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { nome, descricao, icone, ordem, situacao } = this.formulario.value;

        try {
            const {} = await apiPainelControleControleAcessoGrupoMenuEditar({
                id: this.data.grupoMenuId,
                modulo: this.grupoMenu[0].modulo,
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
