import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialog } from '@angular/material/dialog';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { apiRhCurrentUserAtualizaEmailPessoalService } from 'api/rh/api-rh-current-user-atualiza-email-pessoal.service';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { apiRhCurrentUserValidaEmailPessoalService } from 'api/rh/api-rh-current-user-valida-email-pessoal.service';

@Component({
    selector: 'app-atualizacao-cadastral-email',
    templateUrl: './atualizacao-cadastral-email.component.html',
    styleUrls: ['./atualizacao-cadastral-email.component.scss'],
    standalone: false
})
export class AtualizacaoCadastralEmailComponent {
    form = new FormGroup({
        email_pessoal: new FormControl<string | null>('', [
            Validators.required,
            Validators.email,
        ]),
    });

    formConfirmacao = new FormGroup({
        codigo_email: new FormControl<string | null>('', [
            Validators.required,
            Validators.minLength(6),
        ]),
    });

    mensagem = '';

    passo: 'CADASTRO' | 'CONFIRMACAO' | 'FINALIZACAO' = 'CADASTRO';

    alterar: boolean;

    constructor(
        public dialog: MatDialog,
        private currentUserService: CurrentUserService,
        @Inject(MAT_DIALOG_DATA) public data: any
    ) {
        this.alterar = data.alterar;

        this.currentUserService?.reload().then(() => {
            this.form.patchValue({
                email_pessoal:
                    this.currentUserService?.currentUser?.email_pessoal,
            });
        });
    }

    async abrir(alterar: boolean) {
        await this.currentUserService.load();

        const dialogRef = this.dialog.open(AtualizacaoCadastralEmailComponent, {
            disableClose: !this.emailPessoalVerificado,
            data: { alterar: alterar },
        });
    }

    get emailPessoalVerificado() {
        return this.currentUserService?.currentUser?.email_pessoal_verificado;
    }

    async abrirSeNecessario() {
        const currentUser = await this.currentUserService.load();

        if (currentUser === undefined) return;

        if (currentUser.email_pessoal_verificado) return;

        this.abrir(false);
    }

    getErrorMessage() {
        if (this.form.hasError('required')) {
            return 'Informe um e-mail válido';
        }
    }

    async confirmarCadastro() {
        try {
            this.mensagem = '';
            await apiRhCurrentUserAtualizaEmailPessoalService({
                email_pessoal: this.form.value['email_pessoal'],
            });
            this.passo = 'CONFIRMACAO';
        } catch (e) {
            this.mensagem = e?.response?.data?.message || 'E-mail inválido';
            // this.voltarCadastro();
            console.log(e);
        }
    }

    async voltarCadastro() {
        this.passo = 'CADASTRO';
    }

    async validaCodigo() {
        try {
            this.mensagem = '';
            const response = await apiRhCurrentUserValidaEmailPessoalService({
                codigo_email: this.formConfirmacao.value['codigo_email'],
            });

            this.passo = 'FINALIZACAO';
        } catch (e) {
            this.mensagem = e?.response?.data?.message || 'Código inválido';
            console.log(e);
        }
    }

    async finalizar() {
        this.goClose();
    }

    goClose() {
        this.dialog.closeAll();
    }
}
