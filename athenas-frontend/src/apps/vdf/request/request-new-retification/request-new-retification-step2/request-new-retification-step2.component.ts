import { Component } from '@angular/core';
import {
    FormBuilder,
    FormControl,
    FormGroup,
    Validators,
} from '@angular/forms';
import { Router } from '@angular/router';
import { addDay } from 'utils/add-day';
import { addMinute } from 'utils/add-minute';
import { BehaviorSubject, first, map, mergeMap, take } from 'rxjs';
import { pvfUsufructsVacationConfigsDataSource } from 'datasources/pvf/usufructs-vacation-configs.service.datasource';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import {
    ApiRhPvfConfigRequestsVacationConfigsResponseItem,
    apiRhPvfConfigRequestsVacationConfigs,
} from 'api/rh/api-rh-pvf-config-requests-vacation-configs.service';
import { CurrentUserService } from 'core/current-user/current-user.service';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { apiRhPvfRequestsUsufructsBloodDonationService } from 'api/rh/api-rh-pvf-requests-usufructs-blood-donation.service';
import { apiRhPvfRequestsSchedulesRetifications } from 'api/rh/api-rh-pvf-requests-schedules-retifications.service';
import { RequestNewVacationsStep2Component } from '../../request-new-vacations/request-new-vacations-step2/request-new-vacations-step2.component';
import { RequestNewVactionsService } from '../../request-new-vacations/request-new-vacations.service';
import { RequestNewRetificationService } from '../request-new-retification.service';

const today = new Date();
const month = today.getMonth();
const year = today.getFullYear();

@Component({
    selector: 'request-new-retification-step2',
    templateUrl: '../../request-new-vacations/request-new-vacations-step2/request-new-vacations-step2.component.html',
    standalone: false
})
export class RequestNewRetificationStep2Component extends RequestNewVacationsStep2Component {
    constructor(
        public requestStepperService: RequestStepperService,
        public currentUserService: CurrentUserService,
        public requestNewVactionsService: RequestNewVactionsService,
        public router: Router,
        public requestNewRetificationService: RequestNewRetificationService
    ) {
        super(
            requestStepperService,
            currentUserService,
            requestNewVactionsService,
            router
        );
        this.requestStepperService.currentStep = 1;

        if (this.requestNewRetificationService.usufructs_ids?.length <= 0) {
            this.goBack();
        }
    }

    protected get total_days() {
        return this.requestNewRetificationService.total_days_to_retification;
    }

    goNext() {
        this.requestNewRetificationService.usufructs_in = Object.values(
            this.dates
        ).map((x) => {
            return {
                start_date: x.start,
                end_date: x.end,
                days: x.days,
                sale_usufruct: 0,
                parcel_number: 1,
            };
        });

        const hasSell = this.selectedConfig.indemnity?.length > 0;
        if (hasSell) {
            const sellDay = this.selectedConfig.indemnity[0];
            this.requestNewRetificationService.usufructs_in.push({
                start_date: null,
                end_date: null,
                days: 0,
                sale_usufruct: sellDay,
                parcel_number: 1,
            });
        }
        if (this.currentUserService.isSubstitutable) {
            this.router.navigate(['vdf/solicitacoes/retificacoes', 'step3']);
        } else {
            this.goConfirm();
        }
    }

    async goConfirm() {
        try {
            const response = await this.requestNewRetificationService.confirm();
            this.goRequests();
        } catch (e) {
            this.message = e?.response?.data?.message;
        }
    }

    goBack() {
        this.router.navigate(['vdf/solicitacoes/retificacoes', 'step1']);
    }
}
