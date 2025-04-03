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
import { HomeComponent } from './home.component';
import { homeRoute } from './home.route';
import { HomePendingsComponent } from './home-pendings/home-pendings.component';
import { FullCalendarModule } from '@fullcalendar/angular';
import { MatIconModule } from '@angular/material/icon';
import { HomeCalendarComponent } from './home-calendar/home-calendar.component';
import { HomeLinksComponent } from './home-links/home-links.component';
import { VdfCalendarModule } from '../calendar/calendar.module';
import { MpPdfPreviewModule } from 'components/mp-pdf-preview/mp-pdf-preview.module';

const route: Route[] = [...homeRoute];

@NgModule({
    declarations: [
        HomeComponent,
        HomePendingsComponent,
        HomeCalendarComponent,
        HomeLinksComponent,
    ],
    exports: [HomeComponent],
    providers: [],
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
        MatPaginatorModule,
        MatButtonModule,
        MatSelectModule,
        MatRadioModule,
        MatFormFieldModule,
        FormsModule,
        MatTableModule,
        ReactiveFormsModule,
        MatIconModule,
        MpPdfPreviewModule,
        VdfCalendarModule,
        FullCalendarModule,
        RouterModule.forChild(route),
    ],
})
export class VdfHomeModule {}
