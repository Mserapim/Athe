import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { MatDividerModule } from '@angular/material/divider';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MaterialModule } from 'shared/material/material.module';
import { NotificationToast } from './notification.toast.component';
import { ToastrModule } from 'ngx-toastr';

const DECLARATIONS = [NotificationToast];

@NgModule({
    declarations: DECLARATIONS,
    providers: DECLARATIONS,
    exports: DECLARATIONS,
    imports: [
        CommonModule,
        MaterialModule,
        MatListModule,
        MatDividerModule,
        MatIconModule,
        ToastrModule.forRoot(),
    ],
})
export class NotificationToastModule {}
