import { Component, Inject } from '@angular/core';
import {
    MatDialogRef,
    MAT_DIALOG_DATA,
    MatDialog,
} from '@angular/material/dialog';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { FormControl, FormGroup, Validators } from '@angular/forms';

import {DateAdapter} from "@angular/material/core";
import {gedUpload} from "../../../../../api/ged/api-ged-upload.service";
import {MatSnackBar} from "@angular/material/snack-bar";
import {apiESocialAtualizarCertificado} from "../../../../../api/esocial/api-esocial-atualizar-certificado.service";
import {
    apiESocialBuscarCertificadoAtual
} from "../../../../../api/esocial/api-esocial-buscar-certificado-atual.service";

@Component({
    selector: 'item-tabela-criar-dialog',
    templateUrl: 'atualizar-certificado-dialog.component.html',
    standalone: false
})
export class AtualizarCertificadoDialogComponent {

    message: string = '';
    isLoading: boolean = false;
    fileCertificadoA1 = null;
    fileIdCertificadoA1: number = null;
    fileCertificadoCAs = null;
    fileIdCertificadoCAs: number = null;

    hide: boolean = true;


    constructor(
        private dialogRef: MatDialogRef<AtualizarCertificadoDialogComponent>,
        @Inject(MAT_DIALOG_DATA) public data: any,
        protected currentUserService: CurrentUserService,
        protected dialog: MatDialog,
        protected dateAdapter: DateAdapter<Date>,
        private snackBar: MatSnackBar
    ) {
        this.dateAdapter.setLocale('pt-BR');
    }

    fechar(): void {
        this.dialogRef.close();
    }

    ngOnInit() {
        this.carregarCertificadosAtuais();
        this.formulario.controls.certificado_senha.disable();
    }


    protected formulario = new FormGroup({
        fileCertificadoA1: new FormControl<number | null>(null, []),
        certificado_id: new FormControl<number | null>(null, []),
        fileCertificadoCAs: new FormControl<number | null>(null, []),
        certificado_ca_id: new FormControl<number | null>(null, []),
        certificado_senha: new FormControl<string>('', []),
    });

    async goConfirm() {
        this.message = '';

        const { certificado_id, certificado_ca_id, certificado_senha} = this.formulario.value;

        try {
            this.isLoading = true;
            await apiESocialAtualizarCertificado({
                certificado_id, certificado_ca_id, certificado_senha
            });

            this.dialogRef.close();
        } catch (e: any) {
            this.exibirMensagem('Erro', e?.response?.data?.message);
        } finally {
            this.isLoading = false;
        }
    }

    get isValid() {
        if (this.formulario.value.certificado_ca_id == null && this.formulario.value.certificado_id == null)
            return false;

        if (this.formulario.value.certificado_id && !this.formulario.value.certificado_senha) {
            return false;
        }

        return true;
    }

    async onFileCertificadoA1Input($file) {
        this.fileCertificadoA1 = $file.target.files[0];

        if (this.fileCertificadoA1.type === "pfx" || this.fileCertificadoA1.type === "p12" ||
            this.fileCertificadoA1.type === "application/x-pkcs12") {
            const response = await gedUpload({
                file: this.fileCertificadoA1,
                fileName: this.fileCertificadoA1.name,
            });

            this.formulario.value.fileCertificadoA1 = $file.target.files[0];
            this.formulario.value.certificado_id = response.data.file_id;
            this.fileIdCertificadoA1 = response.data.file_id;
            this.formulario.patchValue({
                certificado_id: response.data.file_id,
            });
            this.formulario.controls.certificado_senha.enable();
        } else {
            this.fileCertificadoA1 = null;
            this.exibirMensagem('Atenção', "Tipo do certificado invalido!");
        }
    }

    exibirMensagem(titulo: string, texto: string, classe: string = 'custom-snackbar') {
        this.snackBar.open(texto, '', {
            duration: 4000,
            horizontalPosition: 'center',
            verticalPosition: 'top',
            panelClass: [classe],
        });
    }

    async onFileCertificadoCAsInput($file) {
        this.fileCertificadoCAs = $file.target.files[0];
        const response = await gedUpload({
            file: this.fileCertificadoCAs,
            fileName: this.fileCertificadoCAs.name,
        });

        this.formulario.value.fileCertificadoCAs = $file.target.files[0];
        this.formulario.value.certificado_ca_id = response.data.file_id;
        this.fileIdCertificadoCAs = response.data.file_id;
        this.formulario.patchValue({
            certificado_ca_id: response.data.file_id,
        });
    }

    async carregarCertificadosAtuais() {
        const {certificado_a1_id, certificado_cas_id, nome_certificado_a1, nome_certificado_cas} =
            await apiESocialBuscarCertificadoAtual();
        this.formulario.value.certificado_ca_id = certificado_cas_id;
        this.formulario.value.certificado_id = certificado_a1_id;
        this.fileCertificadoA1 = {name: nome_certificado_a1}
        this.fileCertificadoCAs = {name: nome_certificado_cas}
    }
}
