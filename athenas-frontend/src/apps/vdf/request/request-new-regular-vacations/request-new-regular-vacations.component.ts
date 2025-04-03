import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { RequestNewBaseComponent } from '../request-new-base/request-new-base.component';
import { RequestStepperService } from '../components/request-stepper/request-stepper.service';
import { CurrentUserService } from 'core/current-user/current-user.service';

@Component({
    selector: 'request-new-regular-vacations',
    templateUrl: '../request-new-base/request-new-base.component.html',
    styleUrls: ['./request-new-regular-vacations.component.scss'],
    standalone: false
})
export class RequestNewRegularVacationsComponent extends RequestNewBaseComponent {
    title = 'Solicitação de férias';
    description = `
    Selecione o periodo aquisitivo e escolha entre usufruto e indenizado, sua solicitação deverá de aprovação do chefe imediato e diretoria geral. Após aprovação de ambos, o DGP deverá efetivar. O adicional de férias é pago no mês anterior ao inicio do usufruto, o indenizado é pago na competência do usufruto. Atos regulatórios Ato 820/2012 PGJ
`;

    constructor(
        protected router: Router,
        protected stepper: RequestStepperService,
        protected currentUserService: CurrentUserService
    ) {
        super(router, stepper);
    }

    ngOnInitView() {
        this.stepper.steps = [
            'Periodos aquisitivos',
            'Combinação de usufrutos',
        ];

        if (
            this.currentUserService.currentUser.is_substitutable !=
            'NO_REQUIRED'
        ) {
            this.stepper.steps.push('Substitutos');
        }

        this.stepper.currentStep = 0;
    }
}
