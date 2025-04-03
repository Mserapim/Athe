import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RequestNewEleitoralComponent } from './request-new-eleitoral.component';
import { RequestNewEleitoralStep2FolgaComponent } from './request-new-eleitoral-step2-folga/request-new-eleitoral-step2-folga.component';
import { RequestNewEleitoralStep3FolgaComponent } from './request-new-eleitoral-step3-folga/request-new-eleitoral-step3-folga.component';
import { RequestNewEleitoralStep4FolgaComponent } from './request-new-eleitoral-step4-folga/request-new-eleitoral-step4-folga.component';
import {requestNewEleitoralComponentRoute} from './request-new-eleitoral.route';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { RequestStepperModule } from '../components/request-stepper/request-stepper.module';
import { RequestSubstitutesModule } from '../components/request-substitutes/request-substitutes.module';
import { RequestNewEleitoralService } from './request-new-eleitoral.service';
import { MaterialModule } from 'shared/material/material.module';
import {RequestNewEleitoralStep1Component} from "./request-new-eleitoral-step1/request-new-eleitoral-step1.component";
import {
    RequestNewEleitoralStep2CreditoComponent
} from "./request-new-eleitoral-step2-credito/request-new-eleitoral-step2-credito.component";
import {MpmtFileUpdateModule} from "../../../../components/mpmt-file-update/mpmt-file-update.module";
import {MpmtBotaoModule} from "../../../../components/mpmt-botao/mpmt-botao.module";

const route: Route[] = [...requestNewEleitoralComponentRoute];

@NgModule({
    declarations: [
        RequestNewEleitoralComponent,
        RequestNewEleitoralStep1Component,
        RequestNewEleitoralStep2FolgaComponent,
        RequestNewEleitoralStep3FolgaComponent,
        RequestNewEleitoralStep4FolgaComponent,
        RequestNewEleitoralStep2CreditoComponent
    ],
    providers: [
        RequestNewEleitoralService,
        RequestNewEleitoralStep2FolgaComponent,
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
        MpmtBotaoModule,
        RouterModule.forChild(route),
    ],
})
export class RequestNewEleitoralModule {}
