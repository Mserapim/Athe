import { Route } from '@angular/router';
import { MinhasDiariasComponent } from './minhas-diarias/minhas-diarias.component';
import { NovaDiariaComponent } from './nova-diaria/nova-diaria.component';
import { NovaDiariaStep1Component } from './nova-diaria/step1/viagem-step1.component';
import { NovaDiariaStep2Component } from './nova-diaria/step2/beneficiarios-step2.component';
import { NovaDiariaStep3Component } from './nova-diaria/step3/destinos-step3.component';


export const MinhasDiariasRoute: Route[] = [
    {
        path: 'minhas-diarias',
        component: MinhasDiariasComponent,
    },
    {
        path: 'minhas-diarias/nova/diaria',
        component: NovaDiariaComponent,
        children: [
            {
                path: 'step1',
                component: NovaDiariaStep1Component,
            },
            {
                path: 'step2',
                component: NovaDiariaStep2Component,
            },
            {
                path: 'step3',
                component: NovaDiariaStep3Component,
            },
        ],
    },
    {
        path: 'minhas-diarias/nova/diaria/:step',
        component: NovaDiariaComponent,
    },
];
