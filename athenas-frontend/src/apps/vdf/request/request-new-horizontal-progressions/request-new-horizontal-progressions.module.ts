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
import { MatDialogModule } from '@angular/material/dialog';
import { MatMenuModule } from '@angular/material/menu';
import { MatInputModule } from '@angular/material/input';
import { MatStepperModule } from '@angular/material/stepper';
import { BrowserModule } from '@angular/platform-browser';
import { MatRadioModule } from '@angular/material/radio';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import {
    MatAutocomplete,
    MatAutocompleteModule,
} from '@angular/material/autocomplete';
import { RequestNewHorizontalProgressionsComponent } from './request-new-horizontal-progressions.component';
import { RequestNewHorizontalProgressionsComponentRoute } from './request-new-horizontal-progressions.route';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MaterialModule } from 'shared/material/material.module';
import { RequestNewHorizontalProgressionsStep1Component } from './request-new-horizontal-progressions-step1/request-new-horizontal-progressions-step1.component';
import { RequestNewHorizontalProgressionsStep2Component } from './request-new-horizontal-progressions-step2/request-new-horizontal-progressions-step2.component';
import { RequestStepperModule } from '../components/request-stepper/request-stepper.module';
import { RequestNewHorizontalProgressionsService } from './request-new-horizontal-progressions.service';

const route: Route[] = [...RequestNewHorizontalProgressionsComponentRoute];

@NgModule({
    declarations: [
        RequestNewHorizontalProgressionsComponent,
        RequestNewHorizontalProgressionsStep1Component,
        RequestNewHorizontalProgressionsStep2Component,
    ],
    providers: [RequestNewHorizontalProgressionsService],
    imports: [
        MaterialModule,
        CommonModule,
        FormsModule,
        LayoutModule,
        MatSelectModule,
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
        MatButtonToggleModule,
        RequestStepperModule,
        RouterModule.forChild(route),
    ],
})
export class RequestNewHorizontalProgressionsModule {}
