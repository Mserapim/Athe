import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from 'layout/layout.module';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MaterialModule } from 'shared/material/material.module';
import { MpmtPicklistComponent } from './mpmt-picklist.component';
import {MatIconModule} from "@angular/material/icon";
import {DragDropModule} from "@angular/cdk/drag-drop";
import { MpmtPickListService } from './mpmt-picklist.service';

const DECLARATIONS = [MpmtPicklistComponent];

@NgModule({
    declarations: DECLARATIONS,
    providers: [MpmtPickListService],
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
export class MpmtPicklistModule {}
