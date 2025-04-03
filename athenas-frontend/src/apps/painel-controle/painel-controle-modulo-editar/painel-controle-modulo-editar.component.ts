import { Component, Inject } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiPainelControleControleAcessoModuloAtualizar } from 'api/painel-controle/api-painel-controle-controle-acesso-modulo-atualizar.service';
import { apiPainelControleControleAcessoModulo } from 'api/painel-controle/api-painel-controle-controle-acesso-modulo.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { Console } from 'console';

class PainelControleModuloEditarComponentData {
    pk: number;
    onClose?: Function;
}

@Component({
    selector: 'painel-controle-modulo-editar',
    templateUrl: 'painel-controle-modulo-editar.component.html',
    standalone: false
})
export class PainelControleModuloEditarComponent extends MpmtFormularioComponent<PainelControleModuloEditarComponentData> {

    selectedIcon: string;

    protected formulario = new FormGroup({
        id: new FormControl<number>(null, [Validators.required]),
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
        protected data: PainelControleModuloEditarComponentData,
        protected dialogRef: MatDialogRef<PainelControleModuloEditarComponentData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    protected async resetarFormulario() {
        super.resetarFormulario();

        try {
            const { nome, descricao, ordem, id, sigla, icone, situacao } =
                await apiPainelControleControleAcessoModulo({
                    id: this.data.pk,
                });

            await this.formulario.patchValue({
                id,
                nome,
                descricao,
                ordem,
                sigla,
                icone,
                situacao,
            });

            this.selectedIcon = icone;
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

        const { id, nome, descricao, ordem, sigla, icone, situacao } = this.formulario.value;

        try {
            const {} = await apiPainelControleControleAcessoModuloAtualizar({
                id,
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

    onIconSelected($event) {
        this.formulario.controls.icone.setValue($event);
    }
}
