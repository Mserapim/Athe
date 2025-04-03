import { Component, Inject, OnInit } from '@angular/core';
import { FormArray, FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { apiDiariasConfigCondicionais } from 'api/diarias/config/api-diarias-config-condicionais.service';
import { apiDiariasConfigEtapas } from 'api/diarias/config/api-diarias-config-etapas.service';
import { apiDiariasConfigFluxoEditar } from 'api/diarias/config/api-diarias-config-fluxo-editar.service';
import { apiDiariasConfigFluxo } from 'api/diarias/config/api-diarias-config-fluxo.service';
import { apiDiariasConfigSituacoes } from 'api/diarias/config/api-diarias-config-situacoes.service';
import { MpmtFormularioComponent } from 'components/mpmt-formulario/mpmt-formulario.component';

class DiariasConfigFluxoGerenciarDestinatariosComponentData {
    pk: number;
    onClose?: Function;
}

@Component({
    selector: 'diarias-config-fluxo-gerenciar-destinatarios',
    templateUrl: 'diarias-config-fluxo-gerenciar-destinatarios.component.html',
    standalone: false
})
export class DiariasConfigFluxoGerenciarDestinatariosComponent extends MpmtFormularioComponent<DiariasConfigFluxoGerenciarDestinatariosComponentData> implements OnInit{
    novoEmail: string = '';
    listaEmails: string[] = [];


    ngOnInit() {
        super.ngOnInit();
        this.carregarEmails();
    }

    constructor(
        @Inject(MAT_DIALOG_DATA)
        protected data: DiariasConfigFluxoGerenciarDestinatariosComponentData,
        protected dialogRef: MatDialogRef<DiariasConfigFluxoGerenciarDestinatariosComponentData>,
        protected snackBar: MatSnackBar
    ) {
        super(data, snackBar, dialogRef);
    }

    adicionarEmail() {
        if (this.novoEmail && this.validarEmail(this.novoEmail)) {
            this.listaEmails.push(this.novoEmail);
            this.novoEmail = '';
        } else {
            this.snackBar.open('Por favor, insira um email válido.', 'Fechar', { duration: 3000 });
        }
    }

    removerEmail(index: number) {
        this.listaEmails.splice(index, 1);
    }

    validarEmail(email: string): boolean {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }


    protected async confirmarFormulario() {
        console.log('Emails a salvar:', this.listaEmails);
        this.fecharFormulario();
        try {
            const {} = await apiDiariasConfigFluxoEditar({
                id: this.data.pk,
                notificar_emails: this.listaEmails
            });
            this.resetarFormulario();
            this.fecharFormulario();
            this.data?.onClose();
        } catch (e: any) {
            const detalheErro = e?.response?.data?.message || '';
            const texto = `Ocorreu um erro inesperado ao salvar o módulo. ${detalheErro}`;
            this.exibirMensagem(
                'Atenção',
                texto
            );
        }
    }

    async carregarEmails() {
        try {
            const response = await apiDiariasConfigFluxo({ id: this.data.pk });
            if (response && response.notificar_emails) {
                this.listaEmails = response.notificar_emails;
            }
        } catch (error) {
            console.error('Erro ao carregar os emails:', error);
            this.snackBar.open('Erro ao carregar os emails!', 'Fechar', { duration: 3000 });
        }
    }
}
