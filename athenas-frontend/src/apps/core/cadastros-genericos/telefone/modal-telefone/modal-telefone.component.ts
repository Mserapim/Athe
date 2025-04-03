import { Component, Inject, ViewChild } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { DateAdapter } from '@angular/material/core';
import { MAT_DIALOG_DATA, MatDialog, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiCoreChoicesFormulario } from 'api/core/api-core-choices-formulario.service';
import { apiRhTelefoneCriar } from 'api/rh/telefone/api-rh-telefone-criar.service';
import { apiRhTelefoneEditar } from 'api/rh/telefone/api-rh-telefone-editar.service';
import { apiRhTelefone } from 'api/rh/telefone/api-rh-telefone.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';
import { MpmtSelecaoFormComponent, MpmtSelecaoFormComponentConfiguracao } from 'components/mpmt-selecao-form/mpmt-selecao-form.component';
import { CoresPadraoEnum } from 'enums/CoresPadraoEnum';
import { ModalButton } from 'layout/mpmt-modal/layout-padrao-modal.component';


class TelefoneModalComponentData {
    id?: number;
    pessoa_id?: number;
    orgao_id?: number;
    onClose?: Function;
}

@Component({
    selector: 'modal-telefone',
    templateUrl: './modal-telefone.component.html',
    styleUrls: ['./modal-telefone.component.scss'],
    standalone: false,
})
export class TelefoneModalComponent extends MpmtFormularioComponent<TelefoneModalComponentData> {

    modalButtons: ModalButton[] = [
        {
            label: 'Salvar',
            action: () => this.confirmarFormulario(),
            disabled: () => !this.formularioValido,
            color: 'white',
            backgroundColor: CoresPadraoEnum.verde
        }
    ];

    loading = true; // Variável de controle para o estado de carregamento

    protected formulario = new FormGroup({
        tipo_telefone: new FormControl<number>(null, [Validators.required]),
        principal: new FormControl<boolean>(false, [Validators.required]),
        publico: new FormControl<boolean>(false, [Validators.required]),
        numero: new FormControl<string>(null, [Validators.required]),
    });

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: TelefoneModalComponentData,
        protected dialogRef: MatDialogRef<TelefoneModalComponentData>,
        protected snackBar: MatSnackBar,
        public dialog: MatDialog,
        protected dateAdapter: DateAdapter<Date>,
    ) {
        super(data, snackBar, dialogRef);
        this.dateAdapter.setLocale('pt-BR');

    }

    ngAfterViewInit() {
        this.loading = false;
    }

    ngOnInit() {
        this.carregarDados();
    }


    async carregarDados() {
        if (this.data.id != null) {
            try {
                const response = await apiRhTelefone({
                    id: this.data.id,
                });

                await this.formulario.patchValue({
                    ...(response as any),

                });

            } catch (e) {
                console.error(e);
                this.exibirMensagem(
                    'Atenção',
                    'Erro inesperado ao carregar os valores do formulário'
                );
            }

        }
    }


    protected async confirmarFormulario() {
        try {

            const {
                tipo_telefone,
                numero,
                principal,
                publico

            } = this.formulario.value;

            let orgao = this.data?.orgao_id
            let pessoa = this.data?.pessoa_id

            if (this.data?.id == null) {

                const result = await apiRhTelefoneCriar({
                    pessoa: pessoa,
                    orgao_geral: orgao,
                    tipo_telefone: tipo_telefone,
                    numero: numero,
                    principal: principal,
                    publico: publico,

                });

            } else {
                const result = await apiRhTelefoneEditar({
                    id: this.data.id,
                    pessoa: pessoa,
                    orgao_geral: orgao,
                    tipo_telefone: tipo_telefone,
                    numero: numero,
                    principal: principal,
                    publico: publico,

                });

            }
            this.fecharFormulario();
            this.data?.onClose();

        } catch (e: any) {
            console.error(e);
            const detalheErro = e?.response?.data?.message || '';
            const texto = `${detalheErro}`;
            this.exibirMensagem('Aviso', texto);
        }
    }



    selecaoTipoTelefone: MpmtSelecaoFormComponentConfiguracao = {
        obterOpcoes: apiCoreChoicesFormulario,
        obterFiltros: payload => {
            return { palavra_chave: payload.palavra_chave, app: 'rh', name: 'TYPE_PHONE', per_page: 100 };
        },
        obterValor: 'valor',
        obterTitulo: 'display',
    };



}