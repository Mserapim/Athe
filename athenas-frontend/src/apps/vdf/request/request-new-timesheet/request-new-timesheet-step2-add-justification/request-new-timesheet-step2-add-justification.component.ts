import { Component, Inject } from '@angular/core';
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
import { gedUpload } from 'api/ged/api-ged-upload.service';
import {
    ApiRhPvfRequestsSendingTimesheetsJustificationPayload,
    apiRhPvfRequestsSendingTimesheetsJustifications,
} from 'api/rh/api-rh-pvf-requests-sending-timesheets-justifications.service';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';
import {
    DateAdapter,
    MAT_DATE_FORMATS,
    MAT_DATE_LOCALE,
} from '@angular/material/core';
import {
    MAT_MOMENT_DATE_ADAPTER_OPTIONS,
    MomentDateAdapter,
} from '@angular/material-moment-adapter';
import { MY_FORMATS } from 'apps/app.component';
import moment from "moment";

class RequestNewTimesheetStep2AddJustificationComponentData {
    requestId: number;
    close: () => void;
}

@Component({
    selector: 'request-new-timesheet-step2-add-justification',
    templateUrl: './request-new-timesheet-step2-add-justification.component.html',
    providers: [
        { provide: MAT_DATE_LOCALE, useValue: 'pt-BR' },
        // `MomentDateAdapter` can be automatically provided by importing `MomentDateModule` in your
        // application's root module. We provide it at the component level here, due to limitations of
        // our example generation script.
        {
            provide: DateAdapter,
            useClass: MomentDateAdapter,
            deps: [MAT_DATE_LOCALE, MAT_MOMENT_DATE_ADAPTER_OPTIONS],
        },
        { provide: MAT_DATE_FORMATS, useValue: MY_FORMATS },
    ],
    standalone: false
})
export class RequestNewTimesheetStep2AddJustificationComponent {
    protected apiService = apiRhPvfRequestsUsufructsServerShiftsService;

    title = 'Incluir justificativa';
    message = '';
    observation = '';
    file = null;
    fileId: number = null;

    form = new FormGroup({
        requestId: new FormControl<number | null>(null, [Validators.required]),
        mode: new FormControl<'DAY' | 'HOUR' | null>('HOUR', []),
        file: new FormControl<File | null>(null, []),
        fileId: new FormControl<number | null>(null, []),
        justification: new FormControl<number | null>(null, [
            Validators.required,
        ]),
        observation: new FormControl<string | null>(null, []),
    });

    formHourMode = new FormGroup({
        dateStart: new FormControl<Date | null>(new Date(), [
            Validators.required,
        ]),
        hour: new FormControl<string | null>('00', [Validators.required]),
        minute: new FormControl<string | null>('00', [Validators.required]),
    });

    formDayMode = new FormGroup({
        dateStart: new FormControl<Date | null>(new Date(), [
            Validators.required,
        ]),
        days: new FormControl<number | null>(1, [Validators.required]),
        dateEnd: new FormControl<Date | null>(new Date(), [
            Validators.required,
        ]),
    });

    justifications: ApiRhPvfConfigRequestsTimesheetsJustificationItensItem[];
    data: ApiRhPvfRequestsIdTeleworksTargetsItem[];

    constructor(
        private router: Router,
        @Inject(MAT_DIALOG_DATA)
        public payload: RequestNewTimesheetStep2AddJustificationComponentData,
        stepper: RequestNewTimesheetStepperService
    ) {
        stepper.currentStep = 2;

        // Escuta mudanças no modo
        this.form.get('mode')?.valueChanges.subscribe((mode) => {
            if (mode === 'HOUR') {
                this.formHourMode.patchValue({ dateStart: this.formDayMode.value.dateStart });
            } else if (mode === 'DAY') {
                this.formDayMode.patchValue({ dateStart: this.formHourMode.value.dateStart });
                this.formDayMode.patchValue({ dateEnd: addDay(
                        this.formDayMode.value.dateStart,
                        this.formDayMode.value.days - 1
                    ) });
            }
        });
    }

    async ngOnInit() {
        this.form.patchValue({ requestId: this.payload.requestId });
        this.load({ requestId: this.payload.requestId });
    }

    protected async load({ requestId }: { requestId: number }) {
        const { results } =
            await apiRhPvfConfigRequestsTimesheetsJustificationItens({});
        this.justifications = results;
    }

    get isValid() {
        if (!this.form.valid) return false;
        if (this.form.value.mode == 'DAY') {
            if (!this.formDayMode.valid) return false;
        }
        if (this.form.value.mode == 'HOUR') {
            if (!this.formHourMode.valid) return false;
        }
        return true;
    }

    onChangeStartDate($event) {
        if (this.form.value.mode == 'DAY') {
            this.formDayMode.value.dateStart = $event;
            if (
                !this.formDayMode.value.dateStart ||
                !this.formDayMode.value.days
            )
                return;
            this.formDayMode.value.dateEnd = addDay(
                this.formDayMode.value.dateStart,
                this.formDayMode.value.days - 1
            );
        }
    }

    onChangeDays($event) {
        if (this.form.value.mode == 'DAY') {
            this.formDayMode.value.days = $event;
            if (
                !this.formDayMode.value.dateStart ||
                !this.formDayMode.value.days
            )
                return;
            this.formDayMode.value.dateEnd = addDay(
                this.formDayMode.value.dateStart,
                this.formDayMode.value.days - 1
            );
        }
    }

    async onFileInput($file) {
        // console.log(1, $file);
        this.file = $file.target.files[0];
        const response = await gedUpload({
            file: this.file,
            fileName: this.file.name,
        });

        this.form.value.file = $file.target.files[0];
        this.form.controls['fileId'].setValue(response.data.file_id);
        this.fileId = response.data.file_id;
    }

    options = [
        {
            value: 'ALCANCADA',
            label: 'Alcançada',
        },
        {
            value: 'PARCIAL',
            label: 'Parcialmente Alcançada',
        },
        {
            value: 'NAO_ALCANCADA',
            label: 'Não Alcançada',
        },
    ];

    goBack() {
        this.router.navigate([`vdf/solicitacoes/novo/folhaponto`, 'step1']);
    }

    async goNext() {
        const payload: Partial<ApiRhPvfRequestsSendingTimesheetsJustificationPayload> =
            {
                observation: this.form.value.observation,
                request: this.form.value.requestId,
                reason_type: this.form.value.justification,
            };
        if (this.form.value.fileId) payload.attachment = this.form.value.fileId;
        if (this.form.value.mode == 'DAY') {
            payload.start_date = this.formDayMode.value.dateStart;
            payload.end_date = this.formDayMode.value.dateEnd;
        }
        if (this.form.value.mode == 'HOUR') {
            payload.start_date = this.formHourMode.value.dateStart;
            payload.number_hours =
                this.formHourMode.value.hour +
                ':' +
                this.formHourMode.value.minute;
        }

        payload.origem = 1

        try {
            this.message = '';
            const response =
                await apiRhPvfRequestsSendingTimesheetsJustifications(
                    <ApiRhPvfRequestsSendingTimesheetsJustificationPayload>(
                        payload
                    )
                );
            this.payload.close();
        } catch (e: any) {
            this.message = e?.response?.data?.message;
        }
    }

    hours = [0, 1, 2, 3, 4, 5, 6, 7, 8].map((x) => {
        return {
            value: ('' + x).padStart(2, '0'),
            label: ('' + x).padStart(2, '0'),
        };
    });

    minutes = Array.from(Array(60).keys()).map((x) => {
        return {
            value: ('' + x).padStart(2, '0'),
            label: ('' + x).padStart(2, '0'),
        };
    });
}
