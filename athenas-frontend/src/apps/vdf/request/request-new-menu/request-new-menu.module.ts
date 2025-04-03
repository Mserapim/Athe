import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';

import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MaterialModule } from 'shared/material/material.module';
import { RequestNewMenuComponent } from './request-new-menu.component';

const route: Route[] = [];

@NgModule({
    declarations: [RequestNewMenuComponent],
    providers: [RequestNewMenuComponent],
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        FormsModule,
        MatTableModule,
        ReactiveFormsModule,
        MatButtonToggleModule,
        RouterModule.forChild(route),
    ],
})
export class RequestNewMenuModule {}
