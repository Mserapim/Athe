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
import { MatRadioModule } from '@angular/material/radio';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { FullCalendarModule } from '@fullcalendar/angular';
import { MatIconModule } from '@angular/material/icon';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { ReportsRoute } from './reports.route';
import { ReportsComponent } from './reports.component';
import { ReportsPaycheckComponent } from './reports-paycheck/reports-paycheck.component';
import { ReportsTimesheetComponent } from './reports-timesheet/reports-timesheet.component';
import { ReportsCalendarComponent } from './reports-calendar/reports-calendar.component';
import { FuseLoadingBarModule } from '@fuse/components/loading-bar';
import { ReportsApproverComponent } from './reports-approver/reports-approver.component';
import { ReportsDeliveryPointSheetComponent } from './reports-delivery-point-sheet/reports-delivery-point-sheet.component';
import { ReportsServerShiftComponent } from './reports-server-shift/reports-server-shift.component';
import { ReportsFinancialStatementComponent } from './reports-financial-statement/reports-financial-statement.component';
import { ReportsIncomeStatementComponent } from './reports-income-statement/reports-income-statement.component';
import { MpmtChipsAutocompleteModule } from 'components/mpmt-chips-autocomplete/mpmt-chips-autocomplete.module';

const route: Route[] = [...ReportsRoute];

@NgModule({
    declarations: [
        ReportsComponent,
        ReportsPaycheckComponent,
        ReportsTimesheetComponent,
        ReportsCalendarComponent,
        ReportsApproverComponent,
        ReportsDeliveryPointSheetComponent,
        ReportsServerShiftComponent,
        ReportsFinancialStatementComponent,
        ReportsIncomeStatementComponent,
    ],
    exports: [ReportsComponent],
    providers: [],
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        MatStepperModule,
        MatTableModule,
        MatCheckboxModule,
        MatInputModule,
        MatMenuModule,
        MatDialogModule,
        MatDatepickerModule,
        MatNativeDateModule,
        MatAutocompleteModule,
        MatPaginatorModule,
        MatButtonModule,
        MatSelectModule,
        MatRadioModule,
        MatFormFieldModule,
        FormsModule,
        MatTableModule,
        ReactiveFormsModule,
        MatIconModule,
        FullCalendarModule,
        FuseLoadingBarModule,
        MpmtChipsAutocompleteModule,
        RouterModule.forChild(route),
    ],
})
export class VdfReportsModule {}
