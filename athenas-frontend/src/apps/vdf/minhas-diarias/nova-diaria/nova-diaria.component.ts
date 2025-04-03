import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { MpmtStepperService } from 'components/mpmt-stepper/mpmt-stepper.service'; 
import { CurrentUserService } from 'core/current-user/current-user.service';
import { MpmtStepperModule } from 'components/mpmt-stepper/mpmt-stepper.module'; 
import { DiariaStepperService } from '../stepper/diaria-stepper.service';

@Component({
    selector: 'nova-diaria',
    templateUrl: './nova-diaria.component.html',
    styleUrls: ['./nova-diaria.component.scss'],
    standalone: false
})
export class NovaDiariaComponent{
    title = 'Solicitação de diária';
    description = `
    A solicitação de diárias para um beneficiário seguirá em 3 etapas.<br>
    As regras para concessão do benefício obedecerão à Instrução normativa em vigência. <br><br>
    `;

    constructor(
        protected router: Router,
        protected stepper: DiariaStepperService,
        protected currentUserService: CurrentUserService
    ) {
        // super(router, stepper);
        stepper.steps = ['Dados da viagem', 'Beneficiários', 'Trechos de destino',];
    }

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

    ngOnInitView() {
        this.stepper.steps = [
            'Dados da Viagem', 
            'Beneficiarios', 
            'Trechos de Destino',
        ];
        this.stepper.currentStep = 0;
    }

    public irMinhasDiarias() {
        this.stepper.id_viagem = null;
        this.router.navigate(['vdf/minhas-diarias']);
    }
}
