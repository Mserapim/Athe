import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RequestNewElectoralSlackComponent } from './request-new-electoral-slack.component';
import { RequestNewElectoralSlackStep1Component } from './request-new-electoral-slack-step1/request-new-electoral-slack-step1.component';
import { RequestNewElectoralSlackStep2Component } from './request-new-electoral-slack-step2/request-new-electoral-slack-step2.component';
import { RequestNewElectoralSlackStep3Component } from './request-new-electoral-slack-step3/request-new-electoral-slack-step3.component';
import { requestNewElectoralSlackComponentRoute } from './request-new-electoral-slack.route';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { RequestStepperModule } from '../components/request-stepper/request-stepper.module';
import { RequestSubstitutesModule } from '../components/request-substitutes/request-substitutes.module';
import { RequestNewElectoralSlackService } from './request-new-electoral-slack.service';
import { MaterialModule } from 'shared/material/material.module';

const route: Route[] = [...requestNewElectoralSlackComponentRoute];

@NgModule({
    declarations: [
        RequestNewElectoralSlackComponent,
        RequestNewElectoralSlackStep1Component,
        RequestNewElectoralSlackStep2Component,
        RequestNewElectoralSlackStep3Component,
    ],
    providers: [
        RequestNewElectoralSlackService,
        RequestNewElectoralSlackStep1Component,
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
export class RequestNewElectoralSlackModule {}
