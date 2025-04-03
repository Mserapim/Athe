import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Route, RouterModule } from '@angular/router';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { ServerShiftShowComponent } from './server-shift-show.component';
import { MaterialModule } from 'shared/material/material.module';
import { AutocompleteLibModule } from 'angular-ng-autocomplete';

const route: Route[] = [];

@NgModule({
    declarations: [ServerShiftShowComponent],
    exports: [ServerShiftShowComponent],
    providers: [],
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        ReactiveFormsModule,
        MatIconModule,
        MaterialModule,
        AutocompleteLibModule,
        RouterModule.forChild(route),
    ],
})
export class VdfServerShiftShowModule {}
