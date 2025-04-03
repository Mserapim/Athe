import { Route } from '@angular/router';
import { RequestNewTraineesContextComponent } from './request-new-trainees-contest.component';
import { RequestNewTraineesContextStep1Component } from './request-new-trainees-contest-step1/request-new-trainees-contest-step1.component';
import { RequestNewTraineesContextStep2Component } from './request-new-trainees-contest-step2/request-new-trainees-contest-step2.component';
import { RequestNewTraineesContextStep3Component } from './request-new-trainees-contest-step3/request-new-trainees-contest-step3.component';

export const RequestNewTraineesContextComponentRoute: Route[] = [
    {
        path: 'solicitacoes/novo/concurso-estagiario',
        component: RequestNewTraineesContextComponent,
        children: [
            {
                path: 'step1',
                component: RequestNewTraineesContextStep1Component,
            },
            {
                path: 'step2',
                component: RequestNewTraineesContextStep2Component,
            },
            {
                path: 'step3',
                component: RequestNewTraineesContextStep3Component,
            },
        ],
    },
    {
        path: 'solicitacoes/novo/concurso-estagiario/:step',
        component: RequestNewTraineesContextComponent,
    },
];
