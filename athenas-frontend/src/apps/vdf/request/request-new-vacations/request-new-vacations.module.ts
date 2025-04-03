import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { LayoutModule } from 'layout/layout.module';
import { RequestNewVacationsComponent } from './request-new-vacations.component';
import { RequestNewVacationsStep1Component } from './request-new-vacations-step1/request-new-vacations-step1.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { requestNewVacationsComponentRoute } from './request-new-vacations.route';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatDialogModule } from '@angular/material/dialog';
import { MatMenuModule } from '@angular/material/menu';
import { MatInputModule } from '@angular/material/input';
import { MatStepperModule } from '@angular/material/stepper';
import { RequestNewVacationsStepperComponent } from './request-new-vacations-stepper/request-new-vacations-stepper.component';
import { RequestNewVacationsStep2Component } from './request-new-vacations-step2/request-new-vacations-step2.component';
import { RequestNewVacationsStep3Component } from './request-new-vacations-step3/request-new-vacations-step3.component';
import { RequestNewVacationsStep4Component } from './request-new-vacations-step4/request-new-vacations-step4.component';
import { MatRadioModule } from '@angular/material/radio';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { RequestNewVacationsStepperService } from './request-new-vacations-stepper/request-new-vacations-stepper.service';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { RequestStepperModule } from '../components/request-stepper/request-stepper.module';
import { RequestNewVactionsService } from './request-new-vacations.service';
import { AutocompleteLibModule } from 'angular-ng-autocomplete';
import { RequestNewRetificationStep2Component } from '../request-new-retification/request-new-retification-step2/request-new-retification-step2.component';

const route: Route[] = [...requestNewVacationsComponentRoute];

@NgModule({
    declarations: [
        RequestNewVacationsComponent,
        RequestNewVacationsStepperComponent,
        RequestNewVacationsStep1Component,
        RequestNewVacationsStep2Component,
        RequestNewVacationsStep3Component,
        RequestNewVacationsStep4Component,
    ],
    providers: [RequestNewVacationsStepperService, RequestNewVactionsService],
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
        AutocompleteLibModule,
        RequestStepperModule,
        RouterModule.forChild(route),
    ],
})
export class RequestNewVacationsModule {}
