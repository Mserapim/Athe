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
import { calendarRoute } from './calendar.route';
import { CalendarComponent } from './calendar.component';
import { CalendarAdvancedFilterComponent } from './calendar-advanced-filter/calendar-advanced-filter.component';
import { MatCheckboxModule } from '@angular/material/checkbox';
const route: Route[] = [...calendarRoute];

@NgModule({
    declarations: [CalendarAdvancedFilterComponent, CalendarComponent],
    exports: [CalendarComponent],
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
        RouterModule.forChild(route),
    ],
})
export class VdfCalendarModule {}
