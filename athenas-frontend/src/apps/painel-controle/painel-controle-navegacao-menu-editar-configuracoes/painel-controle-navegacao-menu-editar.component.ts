import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiPainelControleControleAcessoMenuEditar } from 'api/painel-controle/api-painel-controle-controle-acesso-menu-editar.service';
import { apiPainelControleControleAcessoMenu } from 'api/painel-controle/api-painel-controle-controle-acesso-menu.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { CoresPadraoEnum } from 'enums/CoresPadraoEnum';
import { ModalButton } from 'layout/mpmt-modal/layout-padrao-modal.component';

export class PainelControleNavegacaoMenuEditarConfiguracaoComponentData {
    onClose?: Function;
    menuId: number;
}

@Component({
    selector: 'painel-controle-navegacao-menu-editar',
    templateUrl: 'painel-controle-navegacao-menu-editar.component.html',
    standalone: false
})
export class PainelControleNavegacaoMenuEditarConfiguracaoComponent extends MpmtFormularioComponent<PainelControleNavegacaoMenuEditarConfiguracaoComponentData> {

    selectedIcon: string;

    protected formulario = new FormGroup({
        nome: new FormControl('', [Validators.required]),
        descricao: new FormControl(''),
        icone: new FormControl('', [Validators.required]),
        url: new FormControl('', [Validators.required]),
        link_de_ajuda: new FormControl(''),
        grupo: new FormControl(0, [Validators.required]),
        ordem: new FormControl(0, [Validators.required]),
        situacao: new FormControl('ATIVO', [Validators.required]),
    });


    constructor(
        @Inject(MAT_DIALOG_DATA) protected data: PainelControleNavegacaoMenuEditarConfiguracaoComponentData,
        protected dialogRef: MatDialogRef<PainelControleNavegacaoMenuEditarConfiguracaoComponentData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    ngOnInit() {
        if (this.data.menuId) {
            this.carregarDadosMenu();
        }
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

    private async carregarDadosMenu() {
        try {
            const menu = await apiPainelControleControleAcessoMenu ({ id: this.data.menuId });
            this.formulario.patchValue({
                nome: menu.nome,
                descricao: menu.descricao,
                icone: menu.icone,
                url: menu.url,
                ordem: menu.ordem,
                situacao: menu.situacao,
                grupo: menu.grupo,
                link_de_ajuda: menu.link_de_ajuda,
            });

            this.selectedIcon = menu.icone;
        } catch (e) {
            console.error('Erro ao carregar dados do menu:', e);
            this.exibirMensagem('Atenção', 'Erro ao carregar dados do menu');
        }
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { nome, descricao, icone, url, ordem, situacao, grupo, link_de_ajuda } = this.formulario.value;

        try {
            const response = await apiPainelControleControleAcessoMenuEditar({
                id: this.data.menuId,
                nome,
                descricao,
                icone,
                url,
                ordem,
                situacao,
                grupo,
                link_de_ajuda,
            });

            this.fecharFormulario();
            this.data?.onClose();
        } catch (e) {
            console.error('Erro ao salvar as alterações:', e);
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
