import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiDiariasConfigEtapas } from 'api/diarias/config/api-diarias-config-etapas.service';
import { apiDiariasGrupoAprovador } from 'api/diarias/config/grupo-aprovador/api-grupo-aprovador';
import { apiDiariasGrupoAprovadorCriar } from 'api/diarias/config/grupo-aprovador/api-grupo-aprovador-criar';
import { apiDiariasGrupoAprovadorEditar } from 'api/diarias/config/grupo-aprovador/api-grupo-aprovador-editar';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';

class DiariasGrupoAprovadorEditarComponentData {
    id: number;
    onClose?: Function;
}

@Component({
    selector: 'diarias-grupo-aprovador-editar',
    templateUrl: 'grupo-aprovador-editar.component.html',
    standalone: false
})
export class DiariasGrupoAprovadorEditarComponent extends MpmtFormularioComponent<DiariasGrupoAprovadorEditarComponentData> {
    grupos: any[] = [];

    protected formulario = new FormGroup({
        id: new FormControl<number>(null, [Validators.required]),
        nome: new FormControl<string>('', [Validators.required]),
        grupos: new FormControl<number[]>([], [Validators.required]),
    });

    ngOnInit() {
        super.ngOnInit();
        this.carregarGrupos();
    }

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: DiariasGrupoAprovadorEditarComponentData,
        protected dialogRef: MatDialogRef<DiariasGrupoAprovadorEditarComponentData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    protected async resetarFormulario() {
        super.resetarFormulario();

        try {
            const { id, nome, grupos } =
                await apiDiariasGrupoAprovador({
                    id: this.data.id,
                });

            this.formulario.patchValue({
                id,
                nome,
                grupos
            });
        } catch (e) {
            console.log(e);
            this.exibirMensagem(
                'Atenção',
                'Erro inesperado ao carregar os valores do formulário.'
            );
        }
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { id, nome, grupos } = this.formulario.value;

        try {
            const {} = await apiDiariasGrupoAprovadorEditar({
                id,
                nome,
                grupos,
            });

            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose();
        } catch (e: any) {
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao salvar o grupo. ${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }
    }

    async carregarGrupos() {
        try {
            this.grupos = await apiDiariasConfigEtapas({});
            console.log(this.grupos)
        } catch (error) {
            console.error('Erro ao carregar as etapas:', error);
            this.exibirMensagem('Erro', 'Não foi possível carregar as etapas');
        }
    }
}
