import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RequestNewExercicioCumulativoComponent } from './request-new-exercicio-cumulativo.component';
import { RequestNewExercicioCumulativoStep1Component } from './request-new-exercicio-cumulativo-step1/request-new-exercicio-cumulativo-step1.component';
import { RequestNewExercicioCumulativoComponentRoute } from './request-new-exercicio-cumulativo.route';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { RequestStepperModule } from '../components/request-stepper/request-stepper.module';
import { RequestSubstitutesModule } from '../components/request-substitutes/request-substitutes.module';
import { RequestNewExercicioCumulativoService } from './request-new-exercicio-cumulativo.service';
import { MaterialModule } from 'shared/material/material.module';

const route: Route[] = [...RequestNewExercicioCumulativoComponentRoute];

@NgModule({
    declarations: [
        RequestNewExercicioCumulativoComponent,
        RequestNewExercicioCumulativoStep1Component,
    ],
    providers: [
        RequestNewExercicioCumulativoService,
        RequestNewExercicioCumulativoStep1Component,
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
        RouterModule.forChild(route),
    ],
})
export class RequestNewExercicioCumulativoModule {}
