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
import { RequestNewVacationsStep3Component } from '../../request-new-vacations/request-new-vacations-step3/request-new-vacations-step3.component';
import {MatSnackBar} from "@angular/material/snack-bar";
import {MatDialog} from "@angular/material/dialog";
import {FuseConfirmationService} from "../../../../../@fuse/services/confirmation";

const today = new Date();
const month = today.getMonth();
const year = today.getFullYear();

@Component({
    selector: 'request-new-retification-step3',
    templateUrl: '../../request-new-vacations/request-new-vacations-step3/request-new-vacations-step3.component.html',
    standalone: false
})
export class RequestNewRetificationStep3Component extends RequestNewVacationsStep3Component {
    constructor(
        public currentUserService: CurrentUserService,
        public requestStepperService: RequestStepperService,
        public router: Router,
        public requestNewRetificationService: RequestNewRetificationService,
        public confirmationService: FuseConfirmationService
    ) {
        super(
            currentUserService,
            requestStepperService,
            router,
            requestNewRetificationService,
            confirmationService
        );
        this.requestStepperService.currentStep = 1;
    }

    ngOnInit() {
        if (this.requestNewRetificationService.usufructs_ids?.length <= 0) {
            this.goBack();
        }

        if (this.requestNewRetificationService.usufructs_in?.length <= 0) {
            this.goBack();
        }

        this.loadExercises().then((a) => {
            this.populateSubstitutes();
        });

        this.loadCandidates();
    }

    goBack() {
        this.router.navigate(['vdf/solicitacoes/retificacoes', 'step2']);
    }

    async goConfirm() {
        try {
            const response = await this.requestNewRetificationService.confirm();
            this.goRequests();
        } catch (e) {
            this.message = e?.response?.data?.message;
        }
    }

    public get isValid() {
        return true;
    }
}
