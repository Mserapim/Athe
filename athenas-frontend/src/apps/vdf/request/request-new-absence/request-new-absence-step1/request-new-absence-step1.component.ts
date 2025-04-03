import { Component } from '@angular/core';
import { FormBuilder, FormControl, Validators } from '@angular/forms';
import { TypeUsufructEnum } from 'enums/type-usufruct.enum';
import { PvfUsufructsAcquisitionPeriodsDataSource } from 'datasources/pvf/usufructs-acquisition-periods.service.datasource';
import { Router } from '@angular/router';
import { RequestNewAbsenceStepperComponent } from '../request-new-absence-stepper-old/request-new-absence-stepper.component';
import { RequestStepperService } from '../../components/request-stepper/request-stepper.service';
import { PvfConfigRequestsAbsencesTypesDataSource } from 'datasources/pvf-config-requests-absences-types.datasource';
import { ConfigRequestsAbsencesTypesEnum } from 'enums/config-requests-absences-types.enum';
import { RequestNewAbsenceService } from '../request-new-absence.service';

@Component({
    selector: 'request-new-absence-step1',
    templateUrl: './request-new-absence-step1.component.html',
    standalone: false
})
export class RequestNewAbsenceStep1Component {
    dataSource: PvfConfigRequestsAbsencesTypesDataSource;
    myControl = new FormControl();

    ngOnInit() {
        this.dataSource = new PvfConfigRequestsAbsencesTypesDataSource();
        this.dataSource.load({
            page: 1,
            per_page: 10,
        });

        this.dataSource.results$;
    }

    constructor(
        requestStepperService: RequestStepperService,
        private router: Router,
        private requestNewAbsenceService: RequestNewAbsenceService
    ) {
        requestStepperService.currentStep = 0;
    }

    goNext() {
        this.requestNewAbsenceService.typeId = this.myControl.value;
        this.requestNewAbsenceService.goStep2();
    }
}
