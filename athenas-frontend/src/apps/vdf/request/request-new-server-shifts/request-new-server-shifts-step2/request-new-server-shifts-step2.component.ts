import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestNewElectoralSlackStep2Component } from '../../request-new-electoral-slack/request-new-electoral-slack-step2/request-new-electoral-slack-step2.component';
import { RequestNewServerShiftsService } from '../request-new-server-shifts.service';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { DateAdapter, MAT_DATE_FORMATS, MAT_DATE_LOCALE } from '@angular/material/core';
import { MAT_MOMENT_DATE_ADAPTER_OPTIONS, MomentDateAdapter } from '@angular/material-moment-adapter';

export const MY_FORMATS = {
    parse: {
        dateInput: 'DD/MM/YYYY',
    },
    display: {
        dateInput: 'DD/MM/YYYY',
        monthYearLabel: 'MMM YYYY',
        dateA11yLabel: 'LL',
        monthYearA11yLabel: 'MMMM YYYY',
    },
};

@Component({
    selector: 'request-new-server-shifts-step2',
    templateUrl: '../../request-new-electoral-slack/request-new-electoral-slack-step2/request-new-electoral-slack-step2.component.html',
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
export class RequestNewServerShiftsStep2Component extends RequestNewElectoralSlackStep2Component {
    constructor(
        router: Router,
        stepper: RequestStepperService,
        service: RequestNewServerShiftsService
    ) {
        super(stepper, router, service);

        this.service.title = 'Plantão de servidor';
        this.service.path = 'plantao-servidor';
    }
}
