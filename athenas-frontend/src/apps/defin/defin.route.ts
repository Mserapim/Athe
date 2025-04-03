import { Route } from '@angular/router';
import { ColaboradorEventualComponent } from './colaboradores-eventuais/colaboradores-eventuais.component';

export const definRoute: Route[] = [
    {
        path: 'colaborador-eventual',
        component: ColaboradorEventualComponent,
    },
];
