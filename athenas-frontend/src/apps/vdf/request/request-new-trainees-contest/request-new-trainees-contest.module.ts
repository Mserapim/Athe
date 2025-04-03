import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatRadioModule } from '@angular/material/radio';
import { RequestNewTraineesContextComponent } from './request-new-trainees-contest.component';
import { RequestNewTraineesContextStep1Component } from './request-new-trainees-contest-step1/request-new-trainees-contest-step1.component';
import { RequestNewTraineesContextStep2Component } from './request-new-trainees-contest-step2/request-new-trainees-contest-step2.component';
import { RequestNewTraineesContextComponentRoute } from './request-new-trainees-contest.route';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { RequestNewTraineesContextService } from './request-new-trainees-contest.service';
import { MaterialModule } from 'shared/material/material.module';
import { RequestStepperModule } from '../components/request-stepper/request-stepper.module';
import { RequestNewTraineesContextStep3Component } from './request-new-trainees-contest-step3/request-new-trainees-contest-step3.component';
import { RequestSubstitutesModule } from '../components/request-substitutes/request-substitutes.module';

const route: Route[] = [...RequestNewTraineesContextComponentRoute];

@NgModule({
    declarations: [
        RequestNewTraineesContextComponent,
        RequestNewTraineesContextStep1Component,
        RequestNewTraineesContextStep2Component,
        RequestNewTraineesContextStep3Component,
    ],
    providers: [RequestNewTraineesContextService],
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        MatPaginatorModule,
        MatButtonModule,
        MatSelectModule,
        MatRadioModule,
        MatFormFieldModule,
        FormsModule,
        MatTableModule,
        RequestStepperModule,
        ReactiveFormsModule,
        MatButtonToggleModule,
        RequestSubstitutesModule,
        RouterModule.forChild(route),
    ],
})
export class RequestNewTraineesContextModule {}
