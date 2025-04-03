import { Component } from '@angular/core';
import { FormControl } from '@angular/forms';
import { Router } from '@angular/router';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import {RequestNewEleitoralService} from "../request-new-eleitoral.service";

@Component({
    selector: 'request-new-absence-step1',
    templateUrl: './request-new-eleitoral-step1.component.html',
    standalone: false
})
export class RequestNewEleitoralStep1Component {
    tiposSolicitacaoEleitoral = [{label: 'Inclusão de direito', value: 1}, {label: 'Usufruto', value: 2}]
    myControl = new FormControl();

    ngOnInit() {

    }

    constructor(
        requestStepperService: RequestStepperService,
        private router: Router,
        private requestNewEleitoralService: RequestNewEleitoralService
    ) {
        requestStepperService.currentStep = 0;
        this.requestNewEleitoralService.typeId = null
    }

    goNext() {
        this.requestNewEleitoralService.typeId = this.myControl.value;
        this.requestNewEleitoralService.goStep2();
    }
}
