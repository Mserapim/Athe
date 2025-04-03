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
import { BehaviorSubject, delay, first, map, mergeMap, take } from 'rxjs';
import { pvfUsufructsVacationConfigsDataSource } from 'datasources/pvf/usufructs-vacation-configs.service.datasource';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { RequestNewRegularVacationsStepperService } from '../request-new-regular-vacations-stepper/request-new-regular-vacations-stepper.service';
import {
    ApiRhPvfConfigRequestsVacationConfigsResponseItem,
    apiRhPvfConfigRequestsVacationConfigs,
} from 'api/rh/api-rh-pvf-config-requests-vacation-configs.service';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { apiRhPvfRequestsUsufructsRegularVacations } from 'api/rh/api-rh-pvf-requests-usufructs-regular-vacations.service';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { DateAdapter, MAT_DATE_FORMATS, MAT_DATE_LOCALE } from '@angular/material/core';
import { MAT_MOMENT_DATE_ADAPTER_OPTIONS, MomentDateAdapter } from '@angular/material-moment-adapter';

const today = new Date();
const month = today.getMonth();
const year = today.getFullYear();

export const MY_FORMATS = {
    parse: {
        dateInput: 'L',
    },
    display: {
        dateInput: 'L',
        monthYearLabel: 'MMM YYYY',
        dateA11yLabel: 'LL',
        monthYearA11yLabel: 'MMMM YYYY',
    },
};

@Component({
    selector: 'request-new-regular-vacations-step2',
    templateUrl: './request-new-regular-vacations-step2.component.html',
    styleUrls: ['./request-new-regular-vacations-step2.component.scss'],
    standalone: false,
    providers: [
        { provide: MAT_DATE_LOCALE, useValue: 'pt-BR' },
        {
            provide: DateAdapter,
            useClass: MomentDateAdapter,
            deps: [MAT_DATE_LOCALE, MAT_MOMENT_DATE_ADAPTER_OPTIONS],
        },
        { provide: MAT_DATE_FORMATS, useValue: MY_FORMATS },
    ], 
})
export class RequestNewRegularVacationsStep2Component {
    public configs = [];
    public options = [];

    public message: string | undefined = undefined;
    dates: {
        [index: string]: {
            start: Date;
            end: Date;
            days: number;
        };
    } = {};

    range = new FormGroup({
        start: new FormControl<Date | null>(null),
        end: new FormControl<Date | null>(null),
    });

    selectedConfig: {
        enjoyment: number[];
        indemnity: number[];
    };

    ngOnInit() {
        this.loadConfigs();
    }

    constructor(
        private requestStepperService: RequestStepperService,
        private _formBuilder: FormBuilder,
        public currentUserService: CurrentUserService,
        private router: Router
    ) {
        this.requestStepperService.currentStep = 1;
    }

    private async loadConfigs() {
        const { results: configs } =
            await apiRhPvfConfigRequestsVacationConfigs({
                total_days: 30,
                type_usufruct: TypeUsufructEnum.FERIAS_REGULAMENTARES,
            });

        this.configs = configs;
        if (this.configs && this.configs.length > 0)
            this.options = configs[0].options;
    }

    get isValid() {
        return (
            Object.values(this.dates)?.length ==
            this.selectedConfig?.enjoyment?.length
        );
    }
    setUsufructDate(index, $event, days) {
        if (!$event.value) {
            this.dates[index] = {
                start: undefined,
                end: undefined,
                days,
            };
            return;
        }

        const start = $event.value;
        const end = addDay(start, +days - 1);

        this.dates[index] = {
            start,
            end,
            days,
        };
    }

    setSelectConfig(configSource) {
        console.log(configSource.value);
        const config = configSource.value;
        this.selectedConfig = config;
        this.dates = {};
    }

    print(option: any) {
        let text = '';
        text += option.enjoyment
            ?.map((days) => {
                return `${days} dias de usufruto(Folga)`;
            })
            .join(', ');
        if (option.indemnity && option.indemnity.length > 0) text += ' + ';
        text += option.indemnity
            .map((days) => {
                return `${days} indenizados(Venda)`;
            })
            .join(', ');
        return text;
    }

    goBack() {
        this.router.navigate([
            'vdf/solicitacoes/novo/ferias-regulamentares',
            'step1',
        ]);
    }

    goNext() {
        if (this.currentUserService.isSubstitutable) {
            this.router.navigate([
                'vdf/solicitacoes/novo/ferias-regulamentares',
                'step3',
            ]);
        } else {
            this.goConfirm();
        }
    }
    goRequests() {
        this.router.navigate(['vdf/solicitacoes']);
    }
    async goConfirm() {
        const payload = {
            observation: '',
            parcel_number: 1,
            usufructs_in: Object.values(this.dates).map((x) => {
                return {
                    start_date: x.start,
                    end_date: x.end,
                    days: x.days,
                    sale_usufruct: 0,
                    parcel_number: 1,
                };
            }),
        };

        const hasSell = this.selectedConfig.indemnity?.length > 0;
        if (hasSell) {
            const sellDay = this.selectedConfig.indemnity[0];
            payload.usufructs_in.push({
                start_date: null,
                end_date: null,
                days: 0,
                sale_usufruct: sellDay,
                parcel_number: 1,
            });
        }

        try {
            const response = await apiRhPvfRequestsUsufructsRegularVacations(
                payload
            );
            this.goRequests();
        } catch (e) {
            this.message = e?.response?.data?.message;
        }
    }
}
