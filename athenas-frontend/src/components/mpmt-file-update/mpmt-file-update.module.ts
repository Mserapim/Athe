import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MpmtFileUpdateComponent } from './mpmt-file-update.component';

@NgModule({
  declarations: [
    MpmtFileUpdateComponent
  ],
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule
  ],
  exports: [
    MpmtFileUpdateComponent
  ]
})
export class MpmtFileUpdateModule { }
