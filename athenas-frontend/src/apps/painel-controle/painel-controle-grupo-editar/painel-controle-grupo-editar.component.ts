import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiPainelControleControleAcessoModuloAtualizar } from 'api/painel-controle/api-painel-controle-controle-acesso-modulo-atualizar.service';
import { apiPainelControleControleAcessoModulo } from 'api/painel-controle/api-painel-controle-controle-acesso-modulo.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { Console } from 'console';
import {
    apiPainelControleControleAcessoGrupo
} from "../../../api/painel-controle/api-painel-controle-controle-acesso-grupo.service";
import {
    apiPainelControleControleAcessoGrupoEditar
} from "../../../api/painel-controle/api-painel-controle-controle-acesso-grupo-editar.service";
import {ListPaginated} from "../../../api/@base/list-paginated";
import { CoresPadraoEnum } from 'enums/CoresPadraoEnum';
import { ModalButton } from 'layout/mpmt-modal/layout-padrao-modal.component';

class PainelControleGrupoEditarComponentData {
    id: number;
    onClose?: Function;
}

@Component({
    selector: 'painel-controle-modulo-editar',
    templateUrl: 'painel-controle-grupo-editar.component.html',
    standalone: false
})
export class PainelControleGrupoEditarComponent extends MpmtFormularioComponent<PainelControleGrupoEditarComponentData> {

    protected formulario = new FormGroup({
        id: new FormControl<number>(null, [Validators.required]),
        nome: new FormControl<string>('', [Validators.required]),
        descricao: new FormControl<string>(''),
        situacao: new FormControl<'ATIVO' | 'INATIVO'>('ATIVO', [
            Validators.required,
        ]),
        grupo_padrao: new FormControl<boolean>(false),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: PainelControleGrupoEditarComponentData,
        protected dialogRef: MatDialogRef<PainelControleGrupoEditarComponentData>,
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
        return 'Editar Grupo de Acesso'
    }



    protected async resetarFormulario() {
        super.resetarFormulario();

        try {
            const { id, nome, descricao, situacao, grupo_padrao } =
                await apiPainelControleControleAcessoGrupo({
                    id: this.data.id,
                });

            await this.formulario.patchValue({
                id,
                nome,
                descricao,
                situacao,
                grupo_padrao
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

        const { id, nome, descricao, situacao, grupo_padrao } = this.formulario.value;

        try {
            const {} = await apiPainelControleControleAcessoGrupoEditar({
                id,
                nome,
                descricao,
                situacao,
                grupo_padrao
            });

            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose();
        } catch (e: any) {
            console.log(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao editar o grupo. ${detalheErro}`;
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
