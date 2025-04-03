import { Component, Inject } from '@angular/core';
import {
    MatDialogRef,
    MAT_DIALOG_DATA,
    MatDialog,
} from '@angular/material/dialog';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { DateAdapter } from '@angular/material/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { addDay } from 'utils/add-day';
import { RhPvfapiRhPvfVendaSubstituicoesDataSource } from '../../../../../../../datasources/rh-pvf-venda-subtituicoes.datasource';
import { SelectionModel } from '@angular/cdk/collections';
import { SelectItem } from '../../../../../../../utils/select-item';
import { PvfConfigRequestsPersonsDataSource } from '../../../../../../../datasources/pvf-config-requests-persons.datasource';
import { pvfConfigParamsDegreeKinshiptDataSource } from '../../../../../../../datasources/pvf-config-params-degree-kinshipt.datasource';
import { pvfConfigParamsTypeDependentsDataSource } from '../../../../../../../datasources/pvf-config-params-type-dependents.datasource';
import { RequestStepperService } from '../../../request-stepper/request-stepper.service';
import { Router } from '@angular/router';
import { gedUpload } from '../../../../../../../api/ged/api-ged-upload.service';
import { apiVdfSolicitacaoAuxCrecheIrCriar } from '../../../../../../../api/vdf/api-vdf-solicitacao-aux-creche-ir-criar.service';
import {
    RequestPersonNewComponent,
    RequestPersonNewComponentData,
} from '../../../request-person-new/request-person-new.component';
import { TipoParentescoEnum } from '../../../../../../../enums/tipo-parentesco.enum';
import moment from 'moment/moment';
import { TipoDependenteIrEnum } from '../../../../../../../enums/tipo-dependente-ir.enum';
import { printDate } from 'utils/print-date';
import { apiVdfDetalhesSolicitacaoAuxilioCrecheIr } from '../../../../../../../api/vdf/api-vdf-solicitacao-aux-creche-ir-detalhes.service';
import { apiVdfSolicitacaoAuxCrecheIrReenviarCriar } from '../../../../../../../api/vdf/api-vdf-solicitacao-aux-creche-ir-reenviar.service';
import { useGedDownload } from '../../../../../../../api/@base/use-ged-download';

@Component({
    selector: 'request-solicitacao-auxilio-creche-ir-editar',
    templateUrl: 'request-solicitacao-auxilio-creche-ir-editar.component.html',
    standalone: false
})
export class RequestSolicitacaoAuxilioCrecheIrEditarComponent {
    dataSource = new RhPvfapiRhPvfVendaSubstituicoesDataSource();
    message: string = '';
    selection = new SelectionModel<any>(true, []);
    observation: string = '';
    printDate = printDate;
    isLoading: boolean = false;
    listaTipoDependente: any[];

    file = null;
    fileId: number = null;

    capacidadeList: SelectItem[] = [
        { label: 'Válido', value: 1 },
        { label: 'Inválido', value: 2 },
    ];

    dependenteAuxCrecheList: SelectItem[] = [
        { label: 'Sim', value: true },
        { label: 'Não', value: false },
    ];
    dependenteListIRRF: SelectItem[] = [
        { label: 'É dependente', value: true },
        { label: 'Não é dependente', value: false },
    ];

    dataSourcePersons: PvfConfigRequestsPersonsDataSource;
    dataSourceDegreeKinshipt: pvfConfigParamsDegreeKinshiptDataSource;
    dataSourceTypeDependents: pvfConfigParamsTypeDependentsDataSource;

    constructor(
        private dialogRef: MatDialogRef<RequestSolicitacaoAuxilioCrecheIrEditarComponent>,
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

    async ngOnInit() {
        this.dataSourceDegreeKinshipt =
            new pvfConfigParamsDegreeKinshiptDataSource();
        this.dataSourceDegreeKinshipt.load({ page: 1, per_page: 50 });

        this.dataSourceTypeDependents =
            new pvfConfigParamsTypeDependentsDataSource();
        this.dataSourceTypeDependents
            .load({ page: 1, per_page: 50 })
            .then((response) => {
                this.dataSourceTypeDependents.results$.subscribe(
                    (results) => (this.listaTipoDependente = results)
                );
            });

        this.dataSourcePersons = new PvfConfigRequestsPersonsDataSource();
        this.dataSourcePersons.load({ page: 1, per_page: 10 });

        this.carregarDados(this.data);
    }

    async carregarDados(dados): Promise<void> {
        try {
            const response = await apiVdfDetalhesSolicitacaoAuxilioCrecheIr({
                id: dados.requestId,
            });
            this.data = response;
        } catch (e) {
            console.error(e);
        }

        this.formulario.patchValue({
            pessoa_familia: this.data.dependente_id,
            data_nascimento: this.data.data_nascimento,
            dependente_aux_creche: this.data.dependente_aux_creche,
            dependente_ir: this.data.dependente_ir,
            capacidade: this.data.capacidade,
            anexo_id: this.data.anexo_id,
            tipo_parentesco: this.data.tipo_parentesco,
            dependente_tipo: this.data.dependente_tipo,
            observacao: this.data.observacao,
        });

        this.onChangeSearch(null, true);
        this.carregarFile();
    }

    protected formulario = new FormGroup({
        pessoa_familia: new FormControl<number | Object | null>(null, [
            Validators.required,
        ]),
        data_nascimento: new FormControl<Date>(null, []),
        dependente_aux_creche: new FormControl<boolean>(false, []),
        dependente_ir: new FormControl<boolean>(null, [Validators.required]),
        capacidade: new FormControl<number>(null, [Validators.required]),
        anexo_id: new FormControl<number>(null, [Validators.required]),
        tipo_parentesco: new FormControl<number>(null, [Validators.required]),
        dependente_tipo: new FormControl<number>(null, []),
        observacao: new FormControl<string>('', []),
    });

    async load() {
        this.dataSource.load({});
    }

    get selected() {
        if (!this.selection.selected) return [];
        return this.selection.selected?.map((x) => x.id);
    }

    carregarFile() {
        this.file = { name: 'Anexo' };
    }

    async onFileInput($file) {
        this.file = $file.target.files[0];
        const response = await gedUpload({
            file: this.file,
            fileName: this.file.name,
        });

        this.formulario.get('anexo_id').setValue(response.data.file_id);
    }

    async goConfirm() {
        this.message = '';
        const {
            pessoa_familia,
            data_nascimento,
            dependente_aux_creche,
            dependente_ir,
            capacidade,
            anexo_id,
            tipo_parentesco,
            dependente_tipo,
            observacao,
        } = this.formulario.value;

        this.data;

        let pessoa_familia_id;

        if (this.formulario.value.pessoa_familia instanceof Object) {
            pessoa_familia_id =
                this.formulario.get('pessoa_familia').value['pk'];
        }

        let id = this.data.pk;

        try {
            this.isLoading = true;
            await apiVdfSolicitacaoAuxCrecheIrReenviarCriar({
                id,
                pessoa_familia_id,
                anexo_id,
                dependente_aux_creche,
                dependente_ir,
                capacidade,
                tipo_parentesco,
                dependente_tipo,
                observacao,
            });

            this.dialogRef.close();
        } catch (e: any) {
            this.message = e?.response?.data?.message;
        } finally {
            this.isLoading = false;
        }
    }

    get isValid() {
        if (
            this.formulario.value.dependente_ir &&
            this.formulario.value.dependente_tipo == null
        ) {
            return false;
        }

        return this.formulario.valid;
    }

    displayFn(pessoa: SelectItem): string {
        return pessoa.label || '';
    }

    onChangeSearch($event, carregarEdicao: boolean) {
        if (this.formulario.value.pessoa_familia instanceof Object) return;

        this.dataSourcePersons.load({
            keyword: this.formulario.value.pessoa_familia || undefined,
            page: 1,
            per_page: 10,
        });

        if (carregarEdicao) {
            this.dataSourcePersons.results$.subscribe((result) =>
                this.onSelectPerson(result.shift())
            );
        }
    }

    openPersonNew() {
        event?.stopPropagation();
        const dialogRef = this.dialog.open(RequestPersonNewComponent, {
            width: '90%',
            data: <RequestPersonNewComponentData>{
                close: (response) => {
                    if (response) this.onSelectPerson(response);
                    dialogRef.close();
                },
            },
        });

        dialogRef.afterClosed().subscribe((result) => {
            if (result) {
            }
        });
    }

    onSelectPerson($event) {
        this.formulario.controls['pessoa_familia'].setValue(
            $event?.option?.value || $event
        );
        this.formulario.controls['data_nascimento'].setValue(
            $event?.option?.value?.data_nascimento || $event?.data_nascimento
        );
    }

    displayFnPessoa(obj) {
        return obj?.name;
    }

    exibirDependenteAuxilioCreche(): boolean {
        if (
            this.formulario.value.data_nascimento &&
            this.formulario.value.tipo_parentesco
        ) {
            const age = this.calculateAge();
            return (
                age <= 6 &&
                this.formulario.value.tipo_parentesco ==
                    TipoParentescoEnum.FILHO_FILHA
            );
        }
        return false;
    }

    calculateAge(): number {
        const birthMoment = moment(this.formulario.value.data_nascimento);
        return moment().diff(birthMoment, 'years');
    }

    async changeTipoParentesco() {
        switch (this.formulario.value.tipo_parentesco) {
            case TipoParentescoEnum.CONJUGE:
                this.listaTipoDependente = [];
                this.formulario.get('dependente_tipo').setValue(null);
                this.dataSourceTypeDependents
                    .load({ page: 1, per_page: 50 })
                    .then((response) => {
                        this.dataSourceTypeDependents.results$.subscribe(
                            (results) =>
                                (this.listaTipoDependente = results.filter(
                                    (result) =>
                                        result['value'] ==
                                        TipoDependenteIrEnum.CONJUGE
                                ))
                        );
                    });
                break;
            case TipoParentescoEnum.COMPANHEIRO:
                this.listaTipoDependente = [];
                this.formulario.get('dependente_tipo').setValue(null);
                this.dataSourceTypeDependents
                    .load({ page: 1, per_page: 50 })
                    .then((response) => {
                        this.dataSourceTypeDependents.results$.subscribe(
                            (results) =>
                                (this.listaTipoDependente = results.filter(
                                    (result) =>
                                        result['value'] ==
                                        TipoDependenteIrEnum.COMPANHEIRO_UNIAO_ESTAVEL
                                ))
                        );
                    });
                break;
            case TipoParentescoEnum.FILHO_FILHA:
                this.listaTipoDependente = [];
                this.formulario.get('dependente_tipo').setValue(null);
                this.dataSourceTypeDependents
                    .load({ page: 1, per_page: 50 })
                    .then((response) => {
                        this.dataSourceTypeDependents.results$.subscribe(
                            (results) =>
                                (this.listaTipoDependente = results.filter(
                                    (result) =>
                                        result['value'] ==
                                            TipoDependenteIrEnum.FILHO_FILHA_ABSOLUTAMENTE_INCAPAZ ||
                                        result['value'] ==
                                            TipoDependenteIrEnum.FILHO_FILHA_NAO_EMANCIPADO_21_ANOS ||
                                        result['value'] ==
                                            TipoDependenteIrEnum.FILHO_FILHA_OU_ENTEADO_ENTEADA_UNIVESITARIO_OU_CURSANDO_ESCOLA_TECNICA_2_GRAU_ATE_24_ANOS
                                ))
                        );
                    });
                break;
            case TipoParentescoEnum.PAI_MAE:
                this.listaTipoDependente = [];
                this.formulario.get('dependente_tipo').setValue(null);
                this.dataSourceTypeDependents
                    .load({ page: 1, per_page: 50 })
                    .then((response) => {
                        this.dataSourceTypeDependents.results$.subscribe(
                            (results) =>
                                (this.listaTipoDependente = results.filter(
                                    (result) =>
                                        result['value'] ==
                                        TipoDependenteIrEnum.PAI_MAE_COM_DEPENDENCIA_ECONOMICA
                                ))
                        );
                    });
                break;
            case TipoParentescoEnum.IRMAO:
                this.listaTipoDependente = [];
                this.formulario.get('dependente_tipo').setValue(null);
                this.dataSourceTypeDependents
                    .load({ page: 1, per_page: 50 })
                    .then((response) => {
                        this.dataSourceTypeDependents.results$.subscribe(
                            (results) =>
                                (this.listaTipoDependente = results.filter(
                                    (result) =>
                                        result['value'] ==
                                            TipoDependenteIrEnum.IRMAO_ABSOLUTAMENTE_INCAPAZ ||
                                        result['value'] ==
                                            TipoDependenteIrEnum.IRMAO_NAO_EMANCIPADO_MENOR_21_ANO_COM_DEPENDENCIA_ECONOMICA_E_GUARDA_JUDICIAL
                                ))
                        );
                    });
                break;
            case TipoParentescoEnum.ENTEADO:
                this.listaTipoDependente = [];
                this.formulario.get('dependente_tipo').setValue(null);
                this.dataSourceTypeDependents
                    .load({ page: 1, per_page: 50 })
                    .then((response) => {
                        this.dataSourceTypeDependents.results$.subscribe(
                            (results) =>
                                (this.listaTipoDependente = results.filter(
                                    (result) =>
                                        result['value'] ==
                                            TipoDependenteIrEnum.ENTEADO_ABSOLUTAMENTE_INCAPAZ ||
                                        result['value'] ==
                                            TipoDependenteIrEnum.ENTEADO_NAO_EMANCIPADO_21_ANOS
                                ))
                        );
                    });
                break;
            case TipoParentescoEnum.MENOR_TUTELADO:
                this.listaTipoDependente = [];
                this.formulario.get('dependente_tipo').setValue(null);
                this.dataSourceTypeDependents
                    .load({ page: 1, per_page: 50 })
                    .then((response) => {
                        this.dataSourceTypeDependents.results$.subscribe(
                            (results) =>
                                (this.listaTipoDependente = results.filter(
                                    (result) =>
                                        result['value'] ==
                                            TipoDependenteIrEnum.MENOR_ABSOLUTAMENTE_INCAPAZ ||
                                        result['value'] ==
                                            TipoDependenteIrEnum.MENOR_TUTELADO_NAO_EMANCIPADO_MENOR_21_ANO_COM_DEPENDENCIA_ECONOMICA_OU_GUARDA_JUDICIAL
                                ))
                        );
                    });
                break;
            case TipoParentescoEnum.EX_CONJUGE:
                this.listaTipoDependente = [];
                this.formulario.get('dependente_tipo').setValue(null);
                this.dataSourceTypeDependents
                    .load({ page: 1, per_page: 50 })
                    .then((response) => {
                        this.dataSourceTypeDependents.results$.subscribe(
                            (results) =>
                                (this.listaTipoDependente = results.filter(
                                    (result) =>
                                        result['value'] ==
                                        TipoDependenteIrEnum.EX_CONJUGE
                                ))
                        );
                    });
                break;
            case TipoParentescoEnum.NETOS:
                this.listaTipoDependente = [];
                this.formulario.get('dependente_tipo').setValue(null);
                this.dataSourceTypeDependents
                    .load({ page: 1, per_page: 50 })
                    .then((response) => {
                        this.dataSourceTypeDependents.results$.subscribe(
                            (results) =>
                                (this.listaTipoDependente = results.filter(
                                    (result) =>
                                        result['value'] ==
                                        TipoDependenteIrEnum.NETO_NETA_NAO_EMANCIPADO_MENOR_21_ANOS_COM_DEPENDENCIA_ECONOMICA_E_GUARDA_JUDICIAL
                                ))
                        );
                    });
                break;
            case TipoParentescoEnum.OUTROS:
                this.listaTipoDependente = [];
                this.formulario.get('dependente_tipo').setValue(null);
                this.dataSourceTypeDependents
                    .load({ page: 1, per_page: 50 })
                    .then((response) => {
                        this.dataSourceTypeDependents.results$.subscribe(
                            (results) =>
                                (this.listaTipoDependente = results.filter(
                                    (result) =>
                                        result['value'] ==
                                        TipoDependenteIrEnum.AGREGADOS_OUTROS
                                ))
                        );
                    });
                break;
            case TipoParentescoEnum.OUTROS_DEPENDENCIA_ECONOMICA:
                this.listaTipoDependente = [];
                this.formulario.get('dependente_tipo').setValue(null);
                this.dataSourceTypeDependents
                    .load({ page: 1, per_page: 50 })
                    .then((response) => {
                        this.dataSourceTypeDependents.results$.subscribe(
                            (results) =>
                                (this.listaTipoDependente = results.filter(
                                    (result) =>
                                        result['value'] ==
                                            TipoDependenteIrEnum.BISAVOS_COM_DEPENDENCIA_ECONOMICA ||
                                        result['value'] ==
                                            TipoDependenteIrEnum.AVOS_COM_DEPENDENCIA_ECONOMICA ||
                                        result['value'] ==
                                            TipoDependenteIrEnum.BISNETO_BISNETA_NAO_EMANCIPADO_MENOR_21_ANOS_COM_DEPENDENCIA_ECONOMICA_E_GUARDA_JUDICIAL
                                ))
                        );
                    });
                break;
        }
    }

    exibirTipoDependenteIr() {
        return this.formulario.value.dependente_ir;
    }

    changeDependenteIR() {
        if (this.formulario.value.dependente_ir == false) {
            this.formulario.get('dependente_tipo').setValue(null);
        }
    }

    public async downloadAnexo() {
        useGedDownload(this.formulario.get('anexo_id').value.toString());
    }
}
