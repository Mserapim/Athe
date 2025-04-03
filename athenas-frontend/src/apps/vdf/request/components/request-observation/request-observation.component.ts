import { Component, Inject, Input, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import {
    MAT_MOMENT_DATE_ADAPTER_OPTIONS,
    MomentDateAdapter,
} from '@angular/material-moment-adapter';
import {
    DateAdapter,
    MAT_DATE_FORMATS,
    MAT_DATE_LOCALE,
} from '@angular/material/core';
import { MAT_DIALOG_DATA, MatDialog } from '@angular/material/dialog';
import { ActivatedRoute, Router } from '@angular/router';
import { MY_FORMATS } from 'apps/app.component';
import {
    ApiRhPvfConfigRequestsTypeResponse,
    apiRhPvfConfigRequestsPersons,
} from 'api/rh/api-rh-pvf-config-requests-persons.service';
import { RhLocationsDataSource } from 'datasources/rh-locations.datasource';
import { RhConfigParamsImigrantConditionsDataSource } from 'datasources/rh-pvf-config-params-imigrant-conditions.datasource';
import { RhConfigParamsImigrantResidencesDataSource } from 'datasources/rh-pvf-config-params-imigrant-residences.datasource';

export class RequestObservationComponentData {
    observation: string;
    close: (response?: any) => void;
}

@Component({
    selector: 'request-observation',
    templateUrl: './request-observation.component.html',
    standalone: false
})
export class RequestObservationComponent implements OnInit {
    constructor(
        private dialog: MatDialog,
        @Inject(MAT_DIALOG_DATA)
        public payload: RequestObservationComponentData
    ) {}

    ngOnInit() {}

    close() {
        if (!this.payload.close) return;
        this.payload.close();
    }

    async goConfirm() {}
}
