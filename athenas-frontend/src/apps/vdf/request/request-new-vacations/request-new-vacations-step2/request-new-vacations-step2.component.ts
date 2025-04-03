import { Component } from '@angular/core';
import {
    FormBuilder,
    FormControl,
    FormGroup,
    Validators,
} from '@angular/forms';
import { Router } from '@angular/router';
import { addDay } from 'utils/add-day';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { apiRhPvfConfigRequestsVacationConfigs } from 'api/rh/api-rh-pvf-config-requests-vacation-configs.service';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { RequestNewVactionsService } from '../request-new-vacations.service';
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

@Component({
    selector: 'request-new-vacations-step2',
    templateUrl: './request-new-vacations-step2.component.html',
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
export class RequestNewVacationsStep2Component {
    public configs = [];
    public options = [];
    public message: string | undefined = undefined;
    public observation: string = null;
    // public parcels = [1, 2, 3, 5, 6, 7, 8, 9, 10];
    // public parcel: number = 1;

    parcels = [2, 3, 4, 5];
    parcel: number = 1;

    dates: {
        [index: string]: {
            start: Date;
            end: Date;
            days: number;
        };
    } = {};

    public range = new FormGroup({
        start: new FormControl<Date | null>(null),
        end: new FormControl<Date | null>(null),
    });

    public selectedConfig: {
        enjoyment: number[];
        indemnity: number[];
    };

    constructor(
        public requestStepperService: RequestStepperService,
        public currentUserService: CurrentUserService,
        public requestNewVactionsService: RequestNewVactionsService,
        public router: Router
    ) {
        this.requestStepperService.currentStep = 1;
    }

    ngOnInit() {
        this.loadConfigs();
    }

    get isMember() {
        return this.currentUserService.isMember;
    }

    get isTrainne() {
        return this.currentUserService.isTrainne;
    }

    get isResidente() {
        return this.currentUserService.isResidente;
    }

    get isValid() {
        return (
            Object.values(this.dates)?.length ==
            this.selectedConfig?.enjoyment?.length
        );
    }

    protected get total_days() {
        return undefined;
    }

    private async loadConfigs() {
        let type_usufruct = TypeUsufructEnum.FERIAS_REGULAMENTARES;
        if (this.isMember) type_usufruct = TypeUsufructEnum.FERIAS_INDIVIDUAIS;
        if (this.isTrainne)
            type_usufruct = TypeUsufructEnum.RECESSO_DE_ESTAGIARIOS;
        if (this.isResidente)
            type_usufruct = TypeUsufructEnum.RECESSO_RESIDENTE;
        const { results: configs } =
            await apiRhPvfConfigRequestsVacationConfigs({
                type_usufruct,
                total_days: this.total_days,
            });

        this.configs = configs;
        if (this.configs && this.configs.length > 0)
            this.options = configs[0].options;
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
        this.router.navigate(['vdf/solicitacoes/novo/ferias', 'step1']);
    }

    goNext() {
        this.requestNewVactionsService.observation = this.observation;

        this.requestNewVactionsService.type = this.isMember
            ? 'INDIVIDUAL'
            : 'REGULAR';

        this.requestNewVactionsService.type = this.isTrainne
            ? 'ESTAGIARIO'
            : this.requestNewVactionsService.type;

        this.requestNewVactionsService.type = this.isResidente
            ? 'RESIDENTE'
            : this.requestNewVactionsService.type;

        const datesArray = Object.values(this.dates);
        this.requestNewVactionsService.usufructs_in = datesArray.map((x, index) => {
            return {
                start_date: x.start,
                end_date: x.end,
                days: x.days,
                sale_usufruct: 0,
                parcel_number: datesArray.length === 1 ? null : index + 1,
            };
        });

        const hasSell = this.selectedConfig.indemnity?.length > 0;
        if (hasSell) {
            const sellDay = this.selectedConfig.indemnity[0];

            this.requestNewVactionsService.usufructs_in.push({
                start_date: null,
                end_date: null,
                days: sellDay,
                sale_usufruct: sellDay,
                parcel_number: this.parcel,
            });
        }

        if (this.currentUserService.isSubstitutable) {
            this.router.navigate(['vdf/solicitacoes/novo/ferias', 'step3']);
        } else {
            this.goConfirm();
        }
    }
    goRequests() {
        this.router.navigate(['vdf/solicitacoes']);
    }
    async goConfirm() {
        try {
            const response = await this.requestNewVactionsService.confirm();
            this.goRequests();
        } catch (e) {
            this.message = e?.response?.data?.message;
        }
    }
}
