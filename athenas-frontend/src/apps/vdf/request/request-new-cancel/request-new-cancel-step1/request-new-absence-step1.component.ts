import { Component } from '@angular/core';
import { FormBuilder, FormControl, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { RequestNewAbsenceService } from '../../request-new-absence/request-new-absence.service';
import { PvfConfigTiposCancelamentoDataSource } from 'datasources/pvf-config-tipos-cancelamento.datasource';
import { ConfigTiposCancelamentosEnum } from 'enums/config-tipos-cancelamento.enum.';

@Component({
    selector: 'request-new-absence-step1',
    templateUrl: './request-new-absence-step1.component.html',
    standalone: false
})
export class RequestNewCancelStep1Component {
    dataSource: PvfConfigTiposCancelamentoDataSource;
    myControl = new FormControl();

    ngOnInit() {
        this.dataSource = new PvfConfigTiposCancelamentoDataSource();
        this.dataSource.load({
            page: 1,
            per_page: 10,
        });

        this.dataSource.results$;
    }

    constructor(
        requestStepperService: RequestStepperService,
        private router: Router
    ) {
        requestStepperService.currentStep = 0;
    }

    public goNext() {
        if (this.myControl.value == ConfigTiposCancelamentosEnum.PROGRAMACAO)
            this.router.navigate([
                'vdf/solicitacoes/cancelamento',
                'step2',
                'programacao',
            ]);

        if (this.myControl.value == ConfigTiposCancelamentosEnum.TELETRABALHO)
            this.router.navigate([
                'vdf/solicitacoes/cancelamento',
                'step2',
                'teletrabalho',
            ]);
    }
}
