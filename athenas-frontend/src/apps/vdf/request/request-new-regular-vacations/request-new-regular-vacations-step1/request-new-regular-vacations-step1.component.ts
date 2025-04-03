import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { baseDatasourceFactory } from 'datasources/base.datasource.factory';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { pvfUsufructsAcquisitionPeriods } from 'services/pvf/usufructs-acquisition-periods.service';
import { RequestsDataSource } from '../../requests/requests.datasource';
import { PvfUsufructsAcquisitionPeriodsDataSource } from 'datasources/pvf/usufructs-acquisition-periods.service.datasource';
import { Router } from '@angular/router';
import { RequestNewRegularVacationsStepperComponent } from '../request-new-regular-vacations-stepper/request-new-regular-vacations-stepper.component';
import { RequestNewRegularVacationsStepperService } from '../request-new-regular-vacations-stepper/request-new-regular-vacations-stepper.service';
import {
    ApiRhPvfConfigRequestsAcquisitionPeriodsItem,
    apiRhPvfConfigRequestsAcquisitionPeriods,
} from 'api/rh/api-rh-pvf-config-requests-acquisition-periods.service';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';

@Component({
    selector: 'request-new-regular-vacations-step1',
    templateUrl: './request-new-regular-vacations-step1.component.html',
    styleUrls: ['./request-new-regular-vacations-step1.component.scss'],
    standalone: false
})
export class RequestNewRegularVacationsStep1Component {
    public results: ApiRhPvfConfigRequestsAcquisitionPeriodsItem[] = [];

    ngOnInit() {
        this.load();
    }

    async load() {
        throw 'será removido RequestNewRegularVacationsStep1Component';
        const { results } = await apiRhPvfConfigRequestsAcquisitionPeriods({
            page: 1,
            per_page: 10,
            type_usufruct: TypeUsufructEnum.FERIAS_REGULAMENTARES,
        });
        this.results = results;
    }
    constructor(
        private requestStepperService: RequestStepperService,
        private _formBuilder: FormBuilder,
        private router: Router
    ) {
        requestStepperService.currentStep = 0;
    }

    get isValid() {
        return this.results.find((x) => x.balance_available > 0);
    }

    goNext() {
        this.router.navigate([
            'vdf/solicitacoes/novo/ferias-regulamentares',
            'step2',
        ]);
    }
}
