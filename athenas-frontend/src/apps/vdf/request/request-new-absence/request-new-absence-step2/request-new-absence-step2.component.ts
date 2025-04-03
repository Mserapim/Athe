import {
    FormControl,
    FormGroup,
    ValidationErrors,
    Validators,
} from '@angular/forms';
import { Router } from '@angular/router';
import { addDay } from 'utils/add-day';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { gedUpload } from 'api/ged/api-ged-upload.service';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { RequestNewAbsenceService } from '../request-new-absence.service';
import { FuseConfirmationConfig, FuseConfirmationService } from "../../../../../@fuse/services/confirmation";
import {ConfigRequestsAbsencesTypesEnum} from "../../../../../enums/config-requests-absences-types.enum";
import {
    RequestSolicitacaoAuxilioCrecheIrEditarComponent
} from "../../components/request-show/request-show-solicitacao-auxilio-creche-ir/request-solicitacao-auxilio-creche-ir-editar/request-solicitacao-auxilio-creche-ir-editar.component";
import {MatDialog} from "@angular/material/dialog";
import {
    RequestSolicitacaoAuxilioCrecheIrDialogComponent
} from "../../components/request-solicitacao-auxilio-creche-ir-dialog/request-solicitacao-auxilio-creche-ir-dialog.component";
import {CoresPadraoEnum} from "../../../../../enums/CoresPadraoEnum";

export abstract class RequestNewAbsenceStep2Component {
    file = null;
    fileId: number = null;
    message: string;

    configConfirmar: FuseConfirmationConfig = {
        title      : 'Auxílio creche / Dependente IRRF',
        message    : 'Deseja solicitar auxílio creche ou IRRF para esse dependente?',
        icon       : {
            show : true,
            name : 'heroicons_outline:exclamation',
            color: 'warn'
        },
        actions    : {
            confirm: {
                show : true,
                label: 'Sim',
                useStyle: true,
                style: {'background-color': CoresPadraoEnum.verde},
                class: 'text-white'
            },
            cancel : {
                show : true,
                label: 'Não'
            }
        },
        dismissible: false
    };

    protected form: any = new FormGroup({
        file: new FormControl<number | null>(null, []),
        fileId: new FormControl<number | null>(null, [Validators.required]),
        start_date: new FormControl<Date | null>(new Date(), [
            Validators.required,
        ]),
        days: new FormControl<number | null>(1, [Validators.required]),
        hours: new FormControl<number | null>(1, [Validators.required]),
        end_date: new FormControl<Date | null>(null, [Validators.required]),
        observation: new FormControl<String | null>(null, []),
        mode: new FormControl<'DAY' | 'HOUR'>('DAY', []),
    });

    constructor(
        private stepper: RequestStepperService,
        protected router: Router,
        private currentUserService: CurrentUserService,
        protected requestNewAbsenceService: RequestNewAbsenceService,
        protected confirmationService: FuseConfirmationService,
        protected dialog: MatDialog
    ) {
        this.stepper.currentStep = 1;
    }

    async onFileInput($file) {
        this.file = $file.target.files[0];
        const response = await gedUpload({
            file: this.file,
            fileName: this.file.name,
        });

        this.form.value.file = $file.target.files[0];
        this.form.value.fileId = response.data.file_id;
        this.fileId = response.data.file_id;
        this.form.patchValue({
            fileId: response.data.file_id,
        });
    }


    onChangeMode($event) {
        this.onChangeStartDate(this.form.value.start_date);
    }

    onChangeStartDate($event) {
        this.form.value.start_date = $event;
        if (!this.form.value.start_date) return;
        if (this.form.value.mode == 'HOUR') {
            if (!this.form.value.start_date) return;
            this.form.value.end_date = addDay($event, 0);
        } else {
            if (!this.form.value.days) return;
            this.form.value.end_date = addDay(
                this.form.value.start_date,
                this.form.value.days - 1
            );
        }
    }

    onChangeDays($event) {
        this.form.value.days = $event;
        if (!this.form.value.start_date || !this.form.value.days) return;

        if (this.form.value.mode == 'HOUR') {
            this.form.value.end_date = addDay(this.form.value.start_date, 0);
        } else {
            this.form.value.end_date = addDay(
                this.form.value.start_date,
                this.form.value.days - 1
            );
        }
    }

    goBack() {
        this.router.navigate(['vdf/solicitacoes/novo/afastamentos', 'step1']);
    }

    goStep3() {
        this.requestNewAbsenceService.payload = this.getPayload();
        this.router.navigate(['vdf/solicitacoes/novo/afastamentos', 'step3']);
    }

    // abstract getPayload(): any;
    // abstract get service(): any;

    get isValid() {
        return this.form.valid;
    }
    public getFormValidationErrors() {
        Object.keys(this.form.controls).forEach((key) => {
            const controlErrors: ValidationErrors = this.form.get(key).errors;
            if (controlErrors != null) {
                Object.keys(controlErrors).forEach((keyError) => {
                    console.log(
                        'Key control: ' +
                            key +
                            ', keyError: ' +
                            keyError +
                            ', err value: ',
                        controlErrors[keyError]
                    );
                });
            }
        });
    }
    async goNext() {
        if (this.currentUserService.isSubstitutable) return this.goStep3();
        else this.goConfirm();
    }

    async goConfirm() {
        this.message = '';
        try {
            this.requestNewAbsenceService.payload = this.getPayload();
            const response = await this.requestNewAbsenceService.confirm();
            if (response) {
                let data = response['data']

                if((this.requestNewAbsenceService.typeId == ConfigRequestsAbsencesTypesEnum.LICENCA_PATERNIDADE ||
                    this.requestNewAbsenceService.typeId == ConfigRequestsAbsencesTypesEnum.LICENCA_MATERNIDADE) &&
                    data['criar_solicitacao_creche_ir'] == true) {

                    let modalConfirm;
                    modalConfirm = this.confirmationService.open(this.configConfirmar);
                    modalConfirm.afterClosed().subscribe((result) => {
                        if (result === 'confirmed') {
                            let anexo_id = this.requestNewAbsenceService.payload.fileId;
                            let dependente_id = this.requestNewAbsenceService.payload.dependent;
                            const dialogRef = this.dialog.open(RequestSolicitacaoAuxilioCrecheIrDialogComponent, {
                                width: '98%',
                                maxWidth: '98vw',
                                maxHeight: '98vh',
                                data: {
                                anexo_id,
                                dependente_id,
                                close: () => {
                                    dialogRef.close();
                                },
                                },
                            });

                            dialogRef.afterClosed().subscribe((result) => {
                                this.router.navigate(['vdf/solicitacoes']);
                            });
                        }
                    });
                }
            }

            this.router.navigate(['vdf/solicitacoes']);

        } catch (e) {
            this.message = e.response?.data?.message;
            console.log(e);
        }
    }

    protected getPayload() {
        return this.form.value;
    }
}
