import { Component, Inject } from '@angular/core';
import {
    MatDialogRef,
    MAT_DIALOG_DATA,
    MatDialog,
} from '@angular/material/dialog';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { FormControl, FormGroup, Validators } from '@angular/forms';

import { printDate } from 'utils/print-date';
import {apiESocialCriarItemTabela} from "../../../../../api/esocial/api-esocial-criar-item-tabela.service";
import {apiESocialListarTabelas} from "../../../../../api/esocial/api-esocial-listar-tabelas.service";
import {DateAdapter} from "@angular/material/core";
import {SelectItem} from "../../../../../utils/select-item";
import {apiESocialListarOpcoesTabela} from "../../../../../api/esocial/api-esocial-listar-opcoes-tabela.service";
import {ChoiceFiltroEnum} from "../../../../../enums/choice-filtro.enum";
import moment from "moment/moment";
import {
    apiESocialQualificacaoCadastralGerarArquivo
} from "../../../../../api/esocial/qualificacao-cadastral/api-esocial-qualificacao-cadastral-gerar-arquivo.service";
import {Documento} from "../../../../../components/mpmt-file-update/mpmt-file-update.component";
import {
    apiESocialQualificacaoCadastralConfirmarQualificacao
} from "../../../../../api/esocial/qualificacao-cadastral/api-esocial-qualificacao-cadastral-confirmar-qualificacao.service";

@Component({
    selector: 'qualificacao-cadastral-confirmar-qualificacao-dialog',
    templateUrl: 'qualificacao-cadastral-confirmar-qualificacao-dialog.component.html',
    standalone: false
})
export class QualificacaoCadastralConfirmarQualificacaoDialogComponent {

    message: string = '';
    isLoading: boolean = false;
    printDate = printDate;

    anexos: any[] = []
    anexos_carregados: Documento[] = []

    constructor(
        private dialogRef: MatDialogRef<QualificacaoCadastralConfirmarQualificacaoDialogComponent>,
        @Inject(MAT_DIALOG_DATA) public data: any,
        protected currentUserService: CurrentUserService,
        protected dialog: MatDialog,
        protected dateAdapter: DateAdapter<Date>
    ) {
        this.dateAdapter.setLocale('pt-BR');
    }

    fechar(): void {
        this.dialogRef.close();
    }

    ngOnInit() {
    }

    protected formulario = new FormGroup({
        naoQualificados: new FormControl<boolean>(false, []),
    });

    async goConfirm() {
        this.message = '';

        try {
            this.isLoading = true;
            await apiESocialQualificacaoCadastralConfirmarQualificacao(this.anexos.shift());

            this.dialogRef.close();
        } catch (e: any) {
            this.message = e?.response?.data?.message;
        } finally {
            this.isLoading = false;
        }
    }

    get isValid() {
        return this.anexos.length > 0;
    }

    protected async receberAnexos(dados: []) {
        this.anexos = dados
    }
}
