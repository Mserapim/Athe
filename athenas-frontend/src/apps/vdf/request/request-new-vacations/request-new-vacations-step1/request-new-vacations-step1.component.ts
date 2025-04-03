import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { baseDatasourceFactory } from 'datasources/base.datasource.factory';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { pvfUsufructsAcquisitionPeriods } from 'services/pvf/usufructs-acquisition-periods.service';
import { RequestsDataSource } from '../../requests/requests.datasource';
import { PvfUsufructsAcquisitionPeriodsDataSource } from 'datasources/pvf/usufructs-acquisition-periods.service.datasource';
import { Router } from '@angular/router';
import { RequestNewVacationsStepperComponent } from '../request-new-vacations-stepper/request-new-vacations-stepper.component';
import { RequestNewVacationsStepperService } from '../request-new-vacations-stepper/request-new-vacations-stepper.service';
import {
    ApiRhPvfConfigRequestsAcquisitionPeriodsItem,
    apiRhPvfConfigRequestsAcquisitionPeriods,
} from 'api/rh/api-rh-pvf-config-requests-acquisition-periods.service';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { printDate } from 'utils/print-date';

@Component({
    selector: 'request-new-vacations-step1',
    templateUrl: './request-new-vacations-step1.component.html',
    styleUrls: ['./request-new-vacations-step1.component.scss'],
    standalone: false
})
export class RequestNewVacationsStep1Component {
    public results: ApiRhPvfConfigRequestsAcquisitionPeriodsItem[] = [];

    ngOnInit() {
        this.load();
    }

    printDate = printDate;

    async load() {
        let typeUsufruct = TypeUsufructEnum.FERIAS_REGULAMENTARES;
        if (this.currentUserService.isMember)
            typeUsufruct = TypeUsufructEnum.FERIAS_INDIVIDUAIS;
        if (this.currentUserService.isTrainne)
            typeUsufruct = TypeUsufructEnum.RECESSO_DE_ESTAGIARIOS;
        if (this.currentUserService.isResidente)
            typeUsufruct = TypeUsufructEnum.RECESSO_RESIDENTE;

        this.currentUserService.currentUser.type_by_possession;
        const { results } = await apiRhPvfConfigRequestsAcquisitionPeriods({
            page: 1,
            per_page: 10,
            type_usufruct: typeUsufruct,
        });
        this.results = results;
    }

    constructor(
        private requestStepperService: RequestStepperService,
        private _formBuilder: FormBuilder,
        private currentUserService: CurrentUserService,
        private router: Router
    ) {
        requestStepperService.currentStep = 0;
    }

    get isValid() {
        return this.results.find((x) => x.balance_available > 0);
    }

    goNext() {
        this.router.navigate(['vdf/solicitacoes/novo/ferias', 'step2']);
    }
}
