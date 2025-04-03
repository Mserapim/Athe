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
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MaterialModule } from 'shared/material/material.module';
import { MpmtStepperComponent } from './mpmt-stepper.component';
import { MpmtStepperService } from './mpmt-stepper.service';

const route: Route[] = [];

@NgModule({
    exports: [MpmtStepperComponent],
    declarations: [MpmtStepperComponent],
    providers: [MpmtStepperService],
    imports: [
        MaterialModule,
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        MatFormFieldModule,
        FormsModule,
        MatTableModule,
        ReactiveFormsModule,
        MatButtonToggleModule,
        RouterModule.forChild(route),
    ],
})
export class MpmtStepperModule {}
