import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { CalendarOptions } from '@fullcalendar/core'; // useful for typechecking
import dayGridPlugin from '@fullcalendar/daygrid';
import { RequestStepperService } from '../components/request-stepper/request-stepper.service';
import { RequestNewBaseComponent } from '../request-new-base/request-new-base.component';
import { CurrentUserService } from 'core/current-user/current-user.service';

@Component({
    selector: 'request-new-retification',
    templateUrl: '../request-new-base/request-new-base.component.html',
    styleUrls: ['../request-new-base/request-new-base.component.scss'],
    standalone: false
})
export class RequestNewReticationComponent extends RequestNewBaseComponent {
    title = 'Solicitação de Retificação';
    description = `
        Informações importantes e relevantes sobre como relacionar ou solicitar o
        cancelamentos, contatos e emails para tirar dúvidas
    `;

    constructor(
        public router: Router,
        stepper: RequestStepperService,
        private currentUserService: CurrentUserService
    ) {
        super(router, stepper);
        stepper.steps = ['Usufruto a retificar', 'Informe novas datas'];
        if (this.currentUserService?.isSubstitutable)
            stepper.steps.push('Substitutos');
    }

    ngOnInit() {}
}
