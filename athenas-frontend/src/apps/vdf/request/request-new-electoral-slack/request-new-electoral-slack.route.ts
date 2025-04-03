import { Route } from '@angular/router';
import { RequestNewElectoralSlackComponent } from './request-new-electoral-slack.component';
import { RequestNewElectoralSlackStep1Component } from './request-new-electoral-slack-step1/request-new-electoral-slack-step1.component';
import { RequestNewElectoralSlackStep2Component } from './request-new-electoral-slack-step2/request-new-electoral-slack-step2.component';
import { RequestNewElectoralSlackStep3Component } from './request-new-electoral-slack-step3/request-new-electoral-slack-step3.component';

export const requestNewElectoralSlackComponentRoute: Route[] = [
    // {
    //     path: 'solicitacoes/novo/dispensa-eleitoral',
    //     component: RequestNewElectoralSlackComponent,
    //     children: [
    //         {
    //             path: 'step1',
    //             component: RequestNewElectoralSlackStep1Component,
    //         },
    //         {
    //             path: 'step2',
    //             component: RequestNewElectoralSlackStep2Component,
    //         },
    //         {
    //             path: 'step3',
    //             component: RequestNewElectoralSlackStep3Component,
    //         },
    //     ],
    // },
    // {
    //     path: 'solicitacoes/novo/dispensa-eleitoral/:step',
    //     component: RequestNewElectoralSlackComponent,
    // },
];
