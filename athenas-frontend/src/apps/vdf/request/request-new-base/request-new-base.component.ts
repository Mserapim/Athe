import { Component, OnInit } from '@angular/core';
import { RequestStepperService } from '../components/request-stepper/request-stepper.service';
import { RequestStepperModule } from '../components/request-stepper/request-stepper.module';
import { Router, RouterModule } from '@angular/router';
@Component({
    selector: 'request-new-base',
    templateUrl: './request-new-base.component.html',
    styleUrls: ['./request-new-base.component.scss'],
    imports: [RequestStepperModule, RouterModule]
})
export class RequestNewBaseComponent {
    title = '';
    description = ``;

    get descriptionFull() {
        return `
        ${this.description}

        <b>Em caso de dúvidas:</b>
        <li>dgp@mpmt.mp.br     </li>
        <li>Gerência de Servidores     </li>
        <li>Gerência de Membros      </li>

        <b>Em caso de dificuldade técnica:</b>
        <li>suporte@mpmt.mp.br</li>
        `;
    }

    constructor(
        protected router: Router,
        protected stepper: RequestStepperService
    ) {}

    public goRequests() {
        this.router.navigate(['vdf/solicitacoes']);
    }
}
