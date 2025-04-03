import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MaterialModule } from 'shared/material/material.module';
import { MpmtPicklistPaginadoApiComponent } from './mpmt-picklist-paginado-api.component';
import {MatIconModule} from "@angular/material/icon";
import {DragDropModule} from "@angular/cdk/drag-drop";
import { MpmtPicklistPaginadoApiService } from './mpmt-picklist-paginado-api.service';

const DECLARATIONS = [MpmtPicklistPaginadoApiComponent];

@NgModule({
    declarations: DECLARATIONS,
    providers: [MpmtPicklistPaginadoApiService],
    exports: DECLARATIONS,
    imports: [
        CommonModule,
        FormsModule,
        LayoutModule,
        MaterialModule,
        MatInputModule,
        FormsModule,
        ReactiveFormsModule,
        MatIconModule,
        DragDropModule
    ],
})
export class MpmtPicklistPaginadoApiModule {}
