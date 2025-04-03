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
import { RequestNewTimesheetStepperService } from '../request-new-timesheet-stepper/request-new-timesheet-stepper.service';
import { apiRhPvfRequestsUsufructsServerShiftsService } from 'api/rh/api-rh-pvf-requests-usufructs-server-shifts.service';
import { RequestNewTimesheetStep1Component } from '../request-new-timesheet-step1/request-new-timesheet-step1.component';
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
import { RequestNewTimesheetStep2AddJustificationComponent } from '../request-new-timesheet-step2-add-justification/request-new-timesheet-step2-add-justification.component';
import { apiRhPvfRequestsIdTimesheetsJustifications } from 'api/rh/api-rh-pvf-requests-id-timesheets-justifications.service';
import { apiRhPvfRequestsIdSendingTimesheetsService } from 'api/rh/api-rh-pvf-requests-id-sending-timesheets.service';
import { RequestNewTimesheetService } from '../request-new-timesheet.service';
import { apiRhPvfRequestsSendingTimesheetsJustificationsDelete } from 'api/rh/api-rh-pvf-requests-sending-timesheets-justifications-delete.service';
import moment from 'moment';

const today = new Date();
const month = today.getMonth();
const year = today.getFullYear();

@Component({
    selector: 'request-new-timesheet-step2',
    templateUrl: './request-new-timesheet-step2.component.html',
    standalone: false
})
export class RequestNewTimesheetStep2Component {
    protected title = 'Informe a justificativa';
    protected apiService = apiRhPvfRequestsUsufructsServerShiftsService;
    protected message = '';
    protected observation = '';

    form: any = {};

    justifications: any[];
    displayedColumns = [
        'reason_type_name',
        'start_date',
        'end_date',
        'number_hours',
        'observation',
        'delete',
    ];

    data: ApiRhPvfRequestsIdTeleworksTargetsItem[];

    constructor(
        private router: Router,
        public dialog: MatDialog,
        stepper: RequestNewTimesheetStepperService,
        private service: RequestNewTimesheetService
    ) {
        stepper.currentStep = 2;
        if (!this.service.requestId) {
            this.goBack();
        }
    }

    async ngOnInit() {
        this.load();
    }

    protected async load() {
        const { results } = await apiRhPvfRequestsIdTimesheetsJustifications({
            id: this.service.requestId,
        });
        this.justifications = results.filter((x) => !x.canceled);
        console.log(this.justifications);
    }

    get isValid() {
        return true;
    }

    getDate(data: string) {
        return moment(data).format('DD/MM/YY');
    }

    async removeJustification(row: any) {
        try {
            await apiRhPvfRequestsSendingTimesheetsJustificationsDelete({
                id: row.pk,
            });
            this.load();
        } catch (e) {
            console.log(e);
        }
    }

    addJustification(): void {
        const dialog = this.dialog.open(
            RequestNewTimesheetStep2AddJustificationComponent,
            {
                data: {
                    requestId: this.service.requestId,
                    close: () => {
                        dialog.close();
                        this.ngOnInit();
                    },
                },
            }
        );
    }

    goBack() {
        this.router.navigate([`vdf/solicitacoes/novo/folhaponto`, 'step1']);
    }

    goRequests() {
        this.router.navigate(['vdf/solicitacoes']);
    }

    async goNext() {
        try {
            const {} = await apiRhPvfRequestsIdSendingTimesheetsService({
                id: this.service.requestId,
            });

            this.goRequests();
        } catch (e) {
            let mensagem = e?.response?.data?.message;
            this.message = mensagem.replace('<br>', '');
        }
    }
}
