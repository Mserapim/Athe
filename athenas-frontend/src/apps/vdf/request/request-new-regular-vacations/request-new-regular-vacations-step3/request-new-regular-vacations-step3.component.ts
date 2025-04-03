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
import { pvfUsufructsVacationConfigs } from 'services/pvf/usufructs-vacation-configs.service';
import { RequestNewRegularVacationsStepperService } from '../request-new-regular-vacations-stepper/request-new-regular-vacations-stepper.service';
import { pvfCandidateSubstitutesDataSource } from 'datasources/pvf-candidate_substitutes.datasource';

const today = new Date();
const month = today.getMonth();
const year = today.getFullYear();

@Component({
    selector: 'request-new-regular-vacations-step3',
    templateUrl: './request-new-regular-vacations-step3.component.html',
    styleUrls: ['./request-new-regular-vacations-step3.component.scss'],
    standalone: false
})
export class RequestNewRegularVacationsStep3Component {
    substituteCandidatesdataSource: pvfCandidateSubstitutesDataSource;
    dataSource: pvfUsufructsVacationConfigsDataSource;

    private configsSubject = new BehaviorSubject<{}[]>([]);
    public configs$ = this.configsSubject.asObservable();
    myControl = new FormControl();
    range = new FormGroup({
        start: new FormControl<Date | null>(null),
        end: new FormControl<Date | null>(null),
    });

    selectedConfig: any;

    ngOnInit() {
        this.dataSource = new pvfUsufructsVacationConfigsDataSource();
        this.substituteCandidatesdataSource =
            new pvfCandidateSubstitutesDataSource();

        this.find();
        this.subscribeResults();
    }

    constructor(
        private requestNewRegularVacationsStepperService: RequestNewRegularVacationsStepperService,
        private _formBuilder: FormBuilder,
        private router: Router
    ) {
        this.requestNewRegularVacationsStepperService.currentStep = 3;
    }

    dates: {
        [index: string]: {
            start: Date;
            end: Date;
            days: number;
        };
    } = {};

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
        const end = addDay(start, +days);

        this.dates[index] = {
            start,
            end,
            days,
        };
    }

    subscribeResults() {
        return this.dataSource.results$.subscribe((results) => {
            if (!results || results.length == 0) return [];
            let configs = [];
            configs = results.map((x: any) => x.options);
            this.configsSubject.next(configs);
        });
    }

    find() {
        this.dataSource.load({
            page: 1,
            per_page: 100,
            type_usufruct: TypeUsufructEnum.FERIAS_REGULAMENTARES,
        });
    }

    select(option) {
        this.selectedConfig = option;
        console.log(option);
    }

    print(option) {
        let text = '';
        text += option.enjoyment
            .map((days) => {
                return `${days} dias de usufruto(Folga)`;
            })
            .join(', ');
        if (option.indemnity && option.indemnity.length > 0) text += ' + ';
        text += option.indemnity
            .map((days) => {
                return `${days} indenizados(Venda)`;
            })
            .join(', ');

        // enjoyment: number[];
        // indemnity: [];
        return text;
    }

    goBack() {
        this.router.navigate([
            'vdf/solicitacoes/novo/ferias-regulamentares',
            'step1',
        ]);
    }

    goNext() {
        this.router.navigate([
            'vdf/solicitacoes/novo/ferias-regulamentares',
            'step3',
        ]);
    }
}
