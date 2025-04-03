import { Component } from '@angular/core';
import { RequestNewElectoralSlackComponent } from '../request-new-electoral-slack/request-new-electoral-slack.component';
import { DateAdapter, MAT_DATE_FORMATS, MAT_DATE_LOCALE } from '@angular/material/core';
import { MAT_MOMENT_DATE_ADAPTER_OPTIONS, MomentDateAdapter } from '@angular/material-moment-adapter';
import { MY_FORMATS } from 'apps/app.component';

@Component({
    selector: 'request-new-server-shifts',
    templateUrl: '../request-new-base/request-new-base.component.html',
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
export class RequestNewServerShiftsComponent extends RequestNewElectoralSlackComponent {
    title = 'Solicitação de Plantão de Servidores';
}
