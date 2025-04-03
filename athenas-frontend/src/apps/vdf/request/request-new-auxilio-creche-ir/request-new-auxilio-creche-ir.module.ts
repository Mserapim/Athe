import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RequestNewAuxilioCrecheIrComponent } from './request-new-auxilio-creche-ir.component';
import { RequestNewAuxilioCrecheIrStep1Component } from './request-new-auxilio-creche-ir-step1/request-new-auxilio-creche-ir-step1.component';
import { RequestNewExercicioCumulativoComponentRoute } from './request-new-auxilio-creche-ir.route';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { RequestStepperModule } from '../components/request-stepper/request-stepper.module';
import { RequestSubstitutesModule } from '../components/request-substitutes/request-substitutes.module';
import { RequestNewAuxilioCrecheIrService } from './request-new-auxilio-creche-ir.service';
import { MaterialModule } from 'shared/material/material.module';
import {MpmtFileUpdateModule} from "../../../../components/mpmt-file-update/mpmt-file-update.module";

const route: Route[] = [...RequestNewExercicioCumulativoComponentRoute];

@NgModule({
    declarations: [
        RequestNewAuxilioCrecheIrComponent,
        RequestNewAuxilioCrecheIrStep1Component,
    ],
    providers: [
        RequestNewAuxilioCrecheIrService,
        RequestNewAuxilioCrecheIrStep1Component,
    ],
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        FormsModule,
        MaterialModule,
        ReactiveFormsModule,
        MatButtonToggleModule,
        RequestStepperModule,
        RequestStepperModule,
        RequestSubstitutesModule,
        MpmtFileUpdateModule,
        RouterModule.forChild(route),
    ],
})
export class RequestNewAuxilioCrecheIrModule {}
