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
import { FullCalendarModule } from '@fullcalendar/angular';
import { MatIconModule } from '@angular/material/icon';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { RequestStepperComponent } from './request-stepper/request-stepper.component';
import { RequestSubstitutesComponent } from './request-substitutes/request-substitutes.component';
import { RequestStepperService } from './request-stepper/request-stepper.service';
import { RequestUserCreateDialog } from './request-user-create-dialog/request-user-create-dialog.component';
import { RequestStepperModule } from './request-stepper/request-stepper.module';
import { MaterialModule } from 'shared/material/material.module';
import { RequestIndeferirDialog } from './request-indeferir-dialog/request-indeferir-dialog.component';
import {
    RequestSolicitacaoAuxilioCrecheIrDialogComponent
} from "./request-solicitacao-auxilio-creche-ir-dialog/request-solicitacao-auxilio-creche-ir-dialog.component";

const route: Route[] = [];

@NgModule({
    declarations: [RequestUserCreateDialog, RequestIndeferirDialog, RequestSolicitacaoAuxilioCrecheIrDialogComponent],
    exports: [RequestUserCreateDialog, RequestStepperModule, RequestSolicitacaoAuxilioCrecheIrDialogComponent],
    providers: [RequestStepperService],
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        MatFormFieldModule,
        FormsModule,
        MatTableModule,
        ReactiveFormsModule,
        MatIconModule,
        FullCalendarModule,
        RequestStepperModule,
        RouterModule.forChild(route),
    ],
})
export class VdfRequestComponentsModule {}
