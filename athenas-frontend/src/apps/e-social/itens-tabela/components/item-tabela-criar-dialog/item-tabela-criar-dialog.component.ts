import { Component, Inject } from '@angular/core';
import {
    MatDialogRef,
    MAT_DIALOG_DATA,
    MatDialog,
} from '@angular/material/dialog';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { FormControl, FormGroup, Validators } from '@angular/forms';

import { printDate } from 'utils/print-date';
import {
    RhPvfapiRhPvfVendaSubstituicoesDataSource
} from "../../../../../datasources/rh-pvf-venda-subtituicoes.datasource";
import {SelectionModel} from "@angular/cdk/collections";
import {
    apiVdfSolicitacaoAuxCrecheIrCriar
} from "../../../../../api/vdf/api-vdf-solicitacao-aux-creche-ir-criar.service";
import {apiESocialCriarItemTabela} from "../../../../../api/esocial/api-esocial-criar-item-tabela.service";
import {apiESocialListarTabelas} from "../../../../../api/esocial/api-esocial-listar-tabelas.service";
import {DateAdapter} from "@angular/material/core";
import {SelectItem} from "../../../../../utils/select-item";
import {apiESocialListarOpcoesTabela} from "../../../../../api/esocial/api-esocial-listar-opcoes-tabela.service";
import {ChoiceFiltroEnum} from "../../../../../enums/choice-filtro.enum";
import moment from "moment/moment";

@Component({
    selector: 'item-tabela-criar-dialog',
    templateUrl: 'item-tabela-criar-dialog.component.html',
    standalone: false
})
export class ItemTabelaCriarDialogComponent {

    message: string = '';
    isLoading: boolean = false;
    tabelasFiltro: any[] = [];
    printDate = printDate;
    opcoes: SelectItem[] = [];

    constructor(
        private dialogRef: MatDialogRef<ItemTabelaCriarDialogComponent>,
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
        apiESocialListarTabelas().then(response => {
            this.tabelasFiltro = response.results
        })

        this.carregarOpcoesTabela();
    }

    carregarOpcoesTabela(keyword?: string) {
        apiESocialListarOpcoesTabela(
            {keyword: keyword,
            choice_filtro: ChoiceFiltroEnum.ESOCIAL_CLASSIF_EMPLOYEE_BY_POSSESSION})
            .then(response => {
                this.opcoes = response.results.map(item => {return {label: item.titulo, value: item.id}})
            })
    }

    protected formulario = new FormGroup({
        codigo: new FormControl<number>(null, [Validators.required]),
        tabela_esocial: new FormControl<number>(null, [Validators.required]),
        info: new FormControl<string>('', []),
        titulo: new FormControl<string>(null, [Validators.required]),
        descricao: new FormControl<string>(null, []),
        inicio_vigencia: new FormControl<string | null>(null, [Validators.required]),
        fim_vigencia: new FormControl<string | null>(null, []),
        opcoes: new FormControl<number[]>([], []),
    });

    async goConfirm() {
        this.message = '';

        this.formulario.controls.inicio_vigencia.setValue(moment(this.formulario.controls.inicio_vigencia.value).format('YYYY-MM-DD'))
        if (this.formulario.controls.fim_vigencia.value) {
            this.formulario.controls.fim_vigencia.setValue(moment(this.formulario.controls.fim_vigencia.value).format('YYYY-MM-DD'))
        }

        const { codigo,
            tabela_esocial,
            info,
            titulo,
            descricao,
            inicio_vigencia,
            fim_vigencia,
            opcoes} = this.formulario.value;

        try {
            this.isLoading = true;
            await apiESocialCriarItemTabela({
                codigo,
                tabela_esocial,
                info,
                titulo,
                descricao,
                inicio_vigencia,
                fim_vigencia,
                opcoes
            });

            this.dialogRef.close();
        } catch (e: any) {
            this.message = e?.response?.data?.message;
        } finally {
            this.isLoading = false;
        }
    }

    get isValid() {
        return this.formulario.valid;
    }

    opcaoSelecionada($event: string[]) {
        let opcoes = $event.map(event => Number(event))
        this.formulario.controls.opcoes.setValue(opcoes);
    }

    filterOpcao($event: string) {
        this.carregarOpcoesTabela($event);
    }
}
