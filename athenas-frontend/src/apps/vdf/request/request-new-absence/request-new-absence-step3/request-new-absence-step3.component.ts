import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { RequestNewAbsenceService } from '../request-new-absence.service';
import {FuseConfirmationConfig, FuseConfirmationService} from "../../../../../@fuse/services/confirmation";
import {CoresPadraoEnum} from "../../../../../enums/CoresPadraoEnum";
import {MatDialog} from "@angular/material/dialog";
import {ConfigRequestsAbsencesTypesEnum} from "../../../../../enums/config-requests-absences-types.enum";
import {
    RequestSolicitacaoAuxilioCrecheIrDialogComponent
} from "../../components/request-solicitacao-auxilio-creche-ir-dialog/request-solicitacao-auxilio-creche-ir-dialog.component";

const today = new Date();
const month = today.getMonth();
const year = today.getFullYear();

@Component({
    selector: 'request-new-absence-step3',
    templateUrl: './request-new-absence-step3.component.html',
    standalone: false
})
export class RequestNewAbsenceStep3Component {
    dates: any[] = [];
    substitutes: any[] = [];
    isValid: boolean = false;

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

    constructor(
        private requestStepperService: RequestStepperService,
        private router: Router,
        private requestNewAbsenceService: RequestNewAbsenceService,
        protected confirmationService: FuseConfirmationService,
        protected dialog: MatDialog
    ) {
        this.requestStepperService.currentStep = 2;
        this.requestNewAbsenceService.message = '';
    }

    buildDates() {
        return [
            {
                start_date: this.requestNewAbsenceService.payload.start_date,
                end_date: this.requestNewAbsenceService.payload.end_date,
                days: this.requestNewAbsenceService.payload.days,
            },
        ];
    }

    ngOnInit() {
        if (!this.requestNewAbsenceService.typeId) this.goStep1();
        if (!this.requestNewAbsenceService.payload) this.goStep1();
        this.dates = this.buildDates();
    }

    goStep1() {
        this.router.navigate(['vdf/solicitacoes/novo/afastamentos', 'step1']);
    }

    goBack() {
        this.requestNewAbsenceService.goStep2();
    }

    async goConfirm() {
        if (!this.isValid) return;
        try {
            this.requestNewAbsenceService.substitutes = this.substitutes;
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

        } catch (e) {}
    }

    get message() {
        return this.requestNewAbsenceService.message;
    }
}
