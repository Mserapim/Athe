import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { LayoutModule } from 'layout/layout.module';
import { RequestNewRegularVacationsComponent } from './request-new-regular-vacations.component';
import { RequestNewRegularVacationsStep1Component } from './request-new-regular-vacations-step1/request-new-regular-vacations-step1.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { requestNewRegularVacationsComponentRoute } from './request-new-regular-vacations.route';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatDialogModule } from '@angular/material/dialog';
import { MatMenuModule } from '@angular/material/menu';
import { MatInputModule } from '@angular/material/input';
import { MatStepperModule } from '@angular/material/stepper';
import { RequestNewRegularVacationsStepperComponent } from './request-new-regular-vacations-stepper/request-new-regular-vacations-stepper.component';
import { RequestNewRegularVacationsStep2Component } from './request-new-regular-vacations-step2/request-new-regular-vacations-step2.component';
import { RequestNewRegularVacationsStep3Component } from './request-new-regular-vacations-step3/request-new-regular-vacations-step3.component';
import { RequestNewRegularVacationsStep4Component } from './request-new-regular-vacations-step4/request-new-regular-vacations-step4.component';
import { BrowserModule } from '@angular/platform-browser';
import { MatRadioModule } from '@angular/material/radio';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { RequestNewRegularVacationsStepperService } from './request-new-regular-vacations-stepper/request-new-regular-vacations-stepper.service';
import {
    MatAutocomplete,
    MatAutocompleteModule,
} from '@angular/material/autocomplete';
import { RequestStepperModule } from '../components/request-stepper/request-stepper.module';

const route: Route[] = [...requestNewRegularVacationsComponentRoute];

@NgModule({
    declarations: [
        RequestNewRegularVacationsComponent,
        RequestNewRegularVacationsStepperComponent,
        RequestNewRegularVacationsStep1Component,
        RequestNewRegularVacationsStep2Component,
        RequestNewRegularVacationsStep3Component,
        RequestNewRegularVacationsStep4Component,
    ],
    providers: [RequestNewRegularVacationsStepperService],
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        MatStepperModule,
        MatTableModule,
        MatInputModule,
        MatMenuModule,
        MatDialogModule,
        MatDatepickerModule,
        MatNativeDateModule,
        MatAutocompleteModule,
        // MatMomentDateModule,
        MatPaginatorModule,
        MatButtonModule,
        MatSelectModule,
        MatRadioModule,
        MatFormFieldModule,
        FormsModule,
        MatTableModule,
        ReactiveFormsModule,
        RequestStepperModule,
        RouterModule.forChild(route),
    ],
})
export class RequestNewRegularVacationsModule {}
