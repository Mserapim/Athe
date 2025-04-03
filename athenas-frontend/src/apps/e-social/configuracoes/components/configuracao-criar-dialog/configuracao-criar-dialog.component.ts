import { Component, Inject } from '@angular/core';
import {
    MatDialogRef,
    MAT_DIALOG_DATA,
    MatDialog,
} from '@angular/material/dialog';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { FormControl, FormGroup, Validators } from '@angular/forms';

import { printDate } from 'utils/print-date';
import {DateAdapter} from "@angular/material/core";
import {SelectItem} from "../../../../../utils/select-item";
import {apiESocialListarEventos} from "../../../../../api/esocial/api-esocial-listar-eventos.service";
import {
    VincularServidoresDialogComponent,
    VincularServidoresDialogComponentData
} from "../vincular-servidores-dialog/vincular-servidores-dialog.component";
import {RhUnidadesAdministrativasDatasource} from "../../../../../datasources/rh-unidades-administrativas.datasource";
import {PvfConfigRequestsPersonsDataSource} from "../../../../../datasources/pvf-config-requests-persons.datasource";
import moment from "moment";
import {apiESocialCriarConfiguracao} from "../../../../../api/esocial/api-esocial-criar-configuracao.service";

@Component({
    selector: 'configuracao-criar-dialog',
    templateUrl: 'configuracao-criar-dialog.component.html',
    standalone: false
})
export class ConfiguracaoCriarDialogComponent {

    message: string = '';
    isLoading: boolean = false;
    ambientes: any[] = [];
    printDate = printDate;
    eventos: SelectItem[] = [];

    dataSourceResponsaveis = new PvfConfigRequestsPersonsDataSource();
    dataSourceResponsaveisSoftwareHouse = new PvfConfigRequestsPersonsDataSource();

    datasourceUnidadesAdministrativas = new RhUnidadesAdministrativasDatasource();

    empregador: any;
    responsavel: any;
    responsavelSoftware: any;

    constructor(
        private dialogRef: MatDialogRef<ConfiguracaoCriarDialogComponent>,
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
        this.ambientes = [{id: 1, titulo: 'Produção'}, {id: 2, titulo: 'Produção restrita'}]

        this.carregarEventos();
    }

    carregarEventos(keyword?: string) {
        apiESocialListarEventos({keyword})
            .then(response => {
            this.eventos = response.results.map(item => {return {label: item.descricao, value: item.id}})
        });
    }

    protected formulario = new FormGroup({
        ambiente: new FormControl<number>(null, [Validators.required]),
        layout_versao: new FormControl<string>(null, [Validators.pattern('^[0-9]+\\.[0-9]+$')]),
        webservice_envio: new FormControl<string>(null, [Validators.required]),
        webservice_consulta: new FormControl<string>(null, [Validators.required]),
        nome_schema_envio: new FormControl<string>(null, [Validators.required]),
        nome_schema_consulta: new FormControl<string>(null, [Validators.required]),
        url_envio: new FormControl<string>(null, [Validators.required]),
        url_consulta: new FormControl<string>(null, [Validators.required]),
        envio_fila: new FormControl<boolean>(false, [Validators.required]),
        servidores_gerados_ids: new FormControl<number[]>([], []),
        eventos_gerados_ids: new FormControl<number[]>([], []),
        orgao_empregador_id: new FormControl<number>(null, [Validators.required]),
        orgao_empregador: new FormControl<any>(null, [Validators.required]),
        responsavel_id: new FormControl<number>(null, [Validators.required]),
        responsavel: new FormControl<any>(null, [Validators.required]),
        responsavel_sowfware_house_id: new FormControl<number>(null, [Validators.required]),
        responsavel_sowfware_house: new FormControl<any>(null, [Validators.required]),
        tabela_iniciais: new FormControl<string | null>(null, [Validators.required]),
        nao_periodicos: new FormControl<string | null>(null, [Validators.required]),
        periodicos: new FormControl<string | null>(null, [Validators.required]),
        sst: new FormControl<string | null>(null, [Validators.required]),
        inicio_vigencia: new FormControl<string | null>(null, [Validators.required]),
        fim_vigencia: new FormControl<string | null>(null, []),
        data_corte_s2231: new FormControl<string | null>(null, [Validators.required]),

        //campos não utilizados mas que seram mandados como []
        eventos_nao_enviados_ids: new FormControl<number[]>([], []),
        servidores_nao_gerados_ids: new FormControl<number[]>([], []),
        beneficiarios_gerados_ids: new FormControl<number[]>([], []),
        beneficiarios_nao_gerados_ids: new FormControl<number[]>([], []),
    });

    async goConfirm() {

        this.converterDatas()

        const { ambiente,
            layout_versao,
            webservice_envio,
            webservice_consulta,
            nome_schema_envio,
            nome_schema_consulta,
            url_envio,
            url_consulta,
            envio_fila,
            servidores_gerados_ids,
            eventos_gerados_ids,
            orgao_empregador_id,
            responsavel_id,
            responsavel_sowfware_house_id,
            tabela_iniciais,
            nao_periodicos,
            periodicos,
            sst,
            inicio_vigencia,
            fim_vigencia,
            data_corte_s2231,
            eventos_nao_enviados_ids,
            servidores_nao_gerados_ids,
            beneficiarios_gerados_ids,
            beneficiarios_nao_gerados_ids
        } = this.formulario.value;

        try {
            this.isLoading = true;
            await apiESocialCriarConfiguracao({
                ambiente,
                layout_versao,
                webservice_envio,
                webservice_consulta,
                nome_schema_envio,
                nome_schema_consulta,
                url_envio,
                url_consulta,
                envio_fila,
                servidores_gerados_ids,
                eventos_gerados_ids,
                orgao_empregador_id,
                responsavel_id,
                responsavel_sowfware_house_id,
                tabela_iniciais,
                nao_periodicos,
                periodicos,
                sst,
                inicio_vigencia,
                fim_vigencia,
                data_corte_s2231,
                eventos_nao_enviados_ids,
                servidores_nao_gerados_ids,
                beneficiarios_gerados_ids,
                beneficiarios_nao_gerados_ids
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

    eventosSelecionados($event: string[]) {
        let eventos = $event.map(event => Number(event))
        this.formulario.controls.eventos_gerados_ids.setValue(eventos);
    }

    filterEventos($event: string) {
        this.carregarEventos($event);
    }

    vincularServidores() {
        this.dialog.open(VincularServidoresDialogComponent, {
            data: <VincularServidoresDialogComponentData>{
                form: this.formulario
            },
            width: '80%',
            height: '90%',
        });
    }

    loadUnidadesAdministrativas(keyword?: string) {
        this.datasourceUnidadesAdministrativas.load({ keyword: keyword, per_page: 12 });
    }
    loadResponsaveis(keyword?: string) {
        this.dataSourceResponsaveis.load({ keyword: keyword, per_page: 12 });
    }
    loadResponsaveisSoftwareHouse(keyword?: string) {
        this.dataSourceResponsaveisSoftwareHouse.load({ keyword: keyword, per_page: 12 });
    }

    displayFnUnidade(unidade: { nome: string }): string {
        return unidade && unidade.nome ? unidade.nome : '';
    }

    displayFn(obj) {
        return obj?.name;
    }

    onResponsavelSoftwareSelected(value: any) {
        this.formulario.patchValue({
            responsavel_sowfware_house_id: value?.pk
        })
    }

    onResponsavelSelected(value: any) {
        this.formulario.patchValue({
            responsavel_id: value?.pk
        })
    }

    onEmpregadorSelected(value: any) {
        this.formulario.patchValue({
            orgao_empregador_id: value?.id
        })
    }

    private converterDatas() {
        if (this.formulario.controls.inicio_vigencia.value) {
            this.formulario.controls.inicio_vigencia.setValue(moment(this.formulario.controls.inicio_vigencia.value).format('YYYY-MM-DD'))
        }

        if (this.formulario.controls.fim_vigencia.value) {
            this.formulario.controls.fim_vigencia.setValue(moment(this.formulario.controls.fim_vigencia.value).format('YYYY-MM-DD'))
        }

        if (this.formulario.controls.data_corte_s2231.value) {
            this.formulario.controls.data_corte_s2231.setValue(moment(this.formulario.controls.data_corte_s2231.value).format('YYYY-MM-DD'))
        }

        if (this.formulario.controls.nao_periodicos.value) {
            this.formulario.controls.nao_periodicos.setValue(moment(this.formulario.controls.nao_periodicos.value).format('YYYY-MM-DD'))
        }

        if (this.formulario.controls.periodicos.value) {
            this.formulario.controls.periodicos.setValue(moment(this.formulario.controls.periodicos.value).format('YYYY-MM-DD'))
        }

        if (this.formulario.controls.sst.value) {
            this.formulario.controls.sst.setValue(moment(this.formulario.controls.sst.value).format('YYYY-MM-DD'))
        }

        if (this.formulario.controls.tabela_iniciais.value) {
            this.formulario.controls.tabela_iniciais.setValue(moment(this.formulario.controls.tabela_iniciais.value).format('YYYY-MM-DD'))
        }
    }
}
