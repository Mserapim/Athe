import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiPainelControleControleAcessoUsuarioAtualizar } from 'api/painel-controle/api-painel-controle-controle-acesso-usuario-atualizar.service';
import { apiPainelControleControleAcessoUsuario } from 'api/painel-controle/api-painel-controle-controle-acesso-usuario.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { Console } from 'console';
import { CoresPadraoEnum } from 'enums/CoresPadraoEnum';
import { ModalButton } from 'layout/mpmt-modal/layout-padrao-modal.component';

class PainelControleUsuarioEditarComponentData {
    pk: number;
    onClose?: Function;
}

@Component({
    selector: 'painel-controle-usuario-editar',
    templateUrl: 'painel-controle-usuario-editar.component.html',
    standalone: false
})
export class PainelControleUsuarioEditarComponent extends MpmtFormularioComponent<PainelControleUsuarioEditarComponentData> {
    protected formulario = new FormGroup({
        id: new FormControl<number>(null, [Validators.required]),
        username: new FormControl<string>('', [Validators.required]),
        nome: new FormControl<string>('', []),
        matricula: new FormControl<number>(null, []),
        categoria_funcional: new FormControl<string>(null, []),
        lotacao: new FormControl<string>(null, []),
        status: new FormControl<boolean>(null, []),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: PainelControleUsuarioEditarComponentData,
        protected dialogRef: MatDialogRef<PainelControleUsuarioEditarComponentData>,
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
        return 'Editar Usuário'
    }


    protected async resetarFormulario() {
        super.resetarFormulario();

        try {
            const { username, id, nome, matricula, categoria_funcional, lotacao, status} =
                await apiPainelControleControleAcessoUsuario({
                    id: this.data.pk,
                });

            await this.formulario.patchValue({
                id,
                username,
                nome,
                matricula,
                categoria_funcional,
                lotacao,
                status,
            });
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

        const { id, username } = this.formulario.value;

        try {
            const {} = await apiPainelControleControleAcessoUsuarioAtualizar({
                id,
                username,
            });

            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose();
        } catch (e: any) {
            console.log(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao salvar o usuário. ${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }
    }

}
