import { Route } from '@angular/router';
import { RequestNewTimesheetComponent } from './request-new-timesheet.component';
import { RequestNewTimesheetStep1Component } from './request-new-timesheet-step1/request-new-timesheet-step1.component';
import { RequestNewTimesheetStep2Component } from './request-new-timesheet-step2/request-new-timesheet-step2.component';

export const RequestNewTimesheetComponentRoute: Route[] = [
    {
        path: 'solicitacoes/novo/folhaponto',
        component: RequestNewTimesheetComponent,
        children: [
            {
                path: 'step1',
                component: RequestNewTimesheetStep1Component,
            },
            {
                path: 'step2',
                component: RequestNewTimesheetStep2Component,
            },
        ],
    },
];
