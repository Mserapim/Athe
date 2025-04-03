import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiPainelControleControleAcessoGrupoCriar } from 'api/painel-controle/api-painel-controle-controle-acesso-grupo-criar.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { CoresPadraoEnum } from 'enums/CoresPadraoEnum';
import { ModalButton } from 'layout/mpmt-modal/layout-padrao-modal.component';

class PainelControleGrupoAcessoNovoComponentData {
    onClose?: Function;
}

@Component({
    selector: 'painel-controle-grupo-acesso-novo',
    templateUrl: 'painel-controle-grupo-novo.component.html',
    standalone: false
})
export class PainelControleGrupoNovoComponent extends MpmtFormularioComponent<PainelControleGrupoAcessoNovoComponentData> {
    protected formulario = new FormGroup({
        nome: new FormControl<string>('', [Validators.required]),
        descricao: new FormControl<string>(''),
        situacao: new FormControl<'ATIVO' | 'INATIVO'>('ATIVO', [
            Validators.required,
        ]),
        grupo_padrao: new FormControl<boolean>(false),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: PainelControleGrupoAcessoNovoComponentData,
        protected dialogRef: MatDialogRef<PainelControleGrupoAcessoNovoComponentData>,
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
        return 'Novo Grupo de Acesso'
    }


    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { nome, descricao, situacao, grupo_padrao } = this.formulario.value;

        try {
            const {} = await apiPainelControleControleAcessoGrupoCriar({
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
            const texto = `Ocorreu um erro inesperado ao salvar o grupo. ${detalheErro}`;
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
