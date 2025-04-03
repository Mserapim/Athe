import { Component, Inject, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiDiariasConfigEtapas } from 'api/diarias/config/api-diarias-config-etapas.service';
import { apiDiariasGrupoAprovadorCriar } from 'api/diarias/config/grupo-aprovador/api-grupo-aprovador-criar';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';

class DiariasGrupoAprovadorNovoComponentData {
    onClose?: Function;
}

@Component({
    selector: 'diarias-grupo-aprovador-novo',
    templateUrl: 'grupo-aprovador-novo.component.html',
    standalone: false
})
export class DiariasGrupoAprovadorNovoComponent extends MpmtFormularioComponent<DiariasGrupoAprovadorNovoComponentData> implements OnInit{
    grupos: any[] = [];

    protected formulario = new FormGroup({
        nome: new FormControl<string>('', [Validators.required]),
        grupos: new FormControl<number[]>([], [Validators.required]),
    });

    ngOnInit() {
        super.ngOnInit();
        this.carregarGrupos();
    }

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: DiariasGrupoAprovadorNovoComponentData,
        protected dialogRef: MatDialogRef<DiariasGrupoAprovadorNovoComponentData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    protected async confirmarFormulario() {
        if (!this.formularioValido) return;

        const { nome, grupos } = this.formulario.value;

        try {
            const {} = await apiDiariasGrupoAprovadorCriar({
                nome,
                grupos
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
