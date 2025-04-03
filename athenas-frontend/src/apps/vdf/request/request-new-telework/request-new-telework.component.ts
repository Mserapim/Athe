import { Component, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { CalendarOptions } from '@fullcalendar/core'; // useful for typechecking
import dayGridPlugin from '@fullcalendar/daygrid';
import { RequestNewBaseComponent } from '../request-new-base/request-new-base.component';
import { RequestStepperService } from '../components/request-stepper/request-stepper.service';

@Component({
    selector: 'request-new-telework',
    templateUrl: '../request-new-base/request-new-base.component.html',
    standalone: false
})
export class RequestNewTeleworkComponent extends RequestNewBaseComponent {
    title = 'Entrega de relatório de teletrabalho';
    description = `
        Informações importantes e relevantes sobre como relacionar ou solicitar o
        cancelamentos, contatos e emails para tirar dúvidas
    `;

    constructor(public router: Router, stepper: RequestStepperService) {
        super(router, stepper);
        stepper.steps = ['Solicitação', 'Metas'];
    }

    ngOnInit() {}
}
