import { Component } from '@angular/core';
import {
    FormBuilder,
    FormControl,
    FormGroup,
    Validators,
} from '@angular/forms';
import { Router } from '@angular/router';
import { addDay } from 'utils/add-day';
import { addMinute } from 'utils/add-minute';
import { BehaviorSubject, first, map, mergeMap, take } from 'rxjs';
import { pvfUsufructsVacationConfigsDataSource } from 'datasources/pvf/usufructs-vacation-configs.service.datasource';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { RequestNewRelatorioTeletrabalhoSemestralStepperService } from '../request-new-relatorio-teletrabalho-semestral-stepper/request-new-relatorio-teletrabalho-semestral-stepper.service';
import { apiRhPvfRequestsUsufructsServerShiftsService } from 'api/rh/api-rh-pvf-requests-usufructs-server-shifts.service';
import { RequestNewRelatorioTeletrabalhoSemestralStep1Component } from '../request-new-relatorio-teletrabalho-semestral-step1/request-new-relatorio-teletrabalho-semestral-step1.component';
import { RequestNewElectoralSlackStep1Component } from '../../request-new-electoral-slack/request-new-electoral-slack-step1/request-new-electoral-slack-step1.component';
import { RequestNewElectoralSlackStep2Component } from '../../request-new-electoral-slack/request-new-electoral-slack-step2/request-new-electoral-slack-step2.component';
import {
    ApiRhPvfRequestsIdTeleworksTargetsItem,
    apiRhPvfRequestsIdTeleworksTargets,
} from 'api/rh/api-rh-pvf-requests-id-teleworks-targets.service';
import {
    ApiRhPvfConfigRequestsTimesheetsJustificationItensItem,
    apiRhPvfConfigRequestsTimesheetsJustificationItens,
} from 'api/rh/api-rh-pvf-requests-timesheets-justification-itens.service';
import { MatDialog } from '@angular/material/dialog';
import { apiRhPvfRequestsIdTimesheetsJustifications } from 'api/rh/api-rh-pvf-requests-id-timesheets-justifications.service';
import { apiRhPvfRequestsIdSendingTimesheetsService } from 'api/rh/api-rh-pvf-requests-id-sending-timesheets.service';
import { RequestNewRelatorioTeletrabalhoSemestralService } from '../request-new-relatorio-teletrabalho-semestral.service';
import { apiRhPvfRequestsSendingTimesheetsJustificationsDelete } from 'api/rh/api-rh-pvf-requests-sending-timesheets-justifications-delete.service';
import { apiRhPvfRequestsTeletrabalhoCancelar } from 'api/rh/api-rh-pvf-requests-teletrabalho-cancelar.service';
import { apiRhPvfRequestsEnviosRelatorioSemestralTeletrabalhosService } from 'api/rh/api-rh-pvf-requests-envios-relatorio-semestral-teletrabalhos.service';

const today = new Date();
const month = today.getMonth();
const year = today.getFullYear();

@Component({
    selector: 'request-new-relatorio-teletrabalho-semestral-step2',
    templateUrl: './request-new-relatorio-teletrabalho-semestral-step2.component.html',
    standalone: false
})
export class RequestNewRelatorioTeletrabalhoSemestralStep2Component {
    protected title = 'Visualize os dados para envio';
    protected mensagem = '';

    form = new FormGroup({
        dificuldades_servidores: new FormControl<string>('', [
            Validators.required,
        ]),
        medidas_dirimir_dificuldades_servidores: new FormControl<string>('', [
            Validators.required,
        ]),
        dificuldades_facilidades_gestor: new FormControl<string>('', [
            Validators.required,
        ]),
        medidas_dirimir_dificuldades_gestor: new FormControl<string>('', [
            Validators.required,
        ]),
        resultados_alcancados: new FormControl<string>('', [
            Validators.required,
        ]),
        sugestoes_melhorias: new FormControl<string>('', [Validators.required]),
    });

    constructor(
        private router: Router,
        public dialog: MatDialog,
        stepper: RequestNewRelatorioTeletrabalhoSemestralStepperService
    ) {
        stepper.currentStep = 2;
    }

    async ngOnInit() {}

    goBack() {
        return this.router.navigate([
            `vdf/solicitacoes/novo/relatorio-teletrabalho-semestral`,
            'step1',
        ]);
    }

    goRequests() {
        this.router.navigate(['vdf/solicitacoes']);
    }

    async goConfirmar() {
        try {
            const {} =
                await apiRhPvfRequestsEnviosRelatorioSemestralTeletrabalhosService(
                    this.form.value as any
                );
            this.goRequests();
        } catch (e) {
            this.mensagem = e?.response?.data?.message;
        }
    }
}
