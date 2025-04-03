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
import { RequestNewSubstitutePromotersComponent } from './request-new-substitute-promoters.component';
import { RequestNewSubstitutePromotersStep1Component } from './request-new-substitute-promoters-step1/request-new-substitute-promoters-step1.component';
import { RequestNewSubstitutePromotersStep2Component } from './request-new-substitute-promoters-step2/request-new-substitute-promoters-step2.component';
import { RequestNewSubstitutePromotersComponentRoute } from './request-new-substitute-promoters.route';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { RequestNewSubstitutePromotersService } from './request-new-substitute-promoters.service';
import { MaterialModule } from 'shared/material/material.module';
import { RequestStepperModule } from '../components/request-stepper/request-stepper.module';
import { RequestNewSubstitutePromotersStep3Component } from './request-new-substitute-promoters-step3/request-new-substitute-promoters-step3.component';
import { RequestSubstitutesModule } from '../components/request-substitutes/request-substitutes.module';

const route: Route[] = [...RequestNewSubstitutePromotersComponentRoute];

@NgModule({
    declarations: [
        RequestNewSubstitutePromotersComponent,
        RequestNewSubstitutePromotersStep1Component,
        RequestNewSubstitutePromotersStep2Component,
        RequestNewSubstitutePromotersStep3Component,
    ],
    providers: [RequestNewSubstitutePromotersService],
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
export class RequestNewSubstitutePromotersModule {}
