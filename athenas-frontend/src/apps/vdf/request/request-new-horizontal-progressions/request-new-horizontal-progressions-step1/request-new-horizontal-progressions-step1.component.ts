import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { RequestNewHorizontalProgressionsService } from '../request-new-horizontal-progressions.service';

@Component({
    selector: 'request-new-horizontal-progressions-step1',
    templateUrl: './request-new-horizontal-progressions-step1.component.html',
    standalone: false
})
export class RequestNewHorizontalProgressionsStep1Component {
    currents = [];
    currentLevel: string;

    nexts = [];
    nextLevel: string;

    constructor(
        private stepper: RequestStepperService,
        private router: Router,
        protected service: RequestNewHorizontalProgressionsService
    ) {
        stepper.currentStep = 0;
    }

    ngOnInit() {
        this.service.loadCurrentes();
        this.service.loadNexts();
    }

    get isValid() {
        return this.service.selectedCurrent && this.service.selectedNext && this.service.termo_aceite == true;
    }

    goNext() {
        this.router.navigate([
            'vdf/solicitacoes/progressao-horizontal/',
            'step2',
        ]);
    }
}
