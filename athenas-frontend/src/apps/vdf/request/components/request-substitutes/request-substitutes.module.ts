import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatFormFieldModule } from '@angular/material/form-field';
import { FullCalendarModule } from '@fullcalendar/angular';
import { MatIconModule } from '@angular/material/icon';
import { MaterialModule } from 'shared/material/material.module';
import { RequestSubstitutesComponent } from './request-substitutes.component';

@NgModule({
    declarations: [RequestSubstitutesComponent],
    exports: [RequestSubstitutesComponent],
    providers: [],
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
    ],
})
export class RequestSubstitutesModule {}
